from __future__ import annotations

import random
import timeit
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Tuple

from multipart.multipart import Field, File, FormParser, parse_options_header

if TYPE_CHECKING:
    from multipart.multipart import FieldProtocol, FileProtocol


class TestFormParser():
    def __init__(self, headers, config={}) -> None:
        # Parse the Content-Type header to get the multipart boundary.
        self.headers = headers
        _, params = parse_options_header(self.headers['Content-Type'])
        self.charset = params.get(b'charset', 'utf-8')
        if isinstance(self.charset, bytes):
            self.charset = self.charset.decode('latin-1')
        try:
            self.boundary = params[b'boundary']
        except KeyError:
            raise Exception('Missing boundary in multipart.')
            
        self.ended = False
        self.files: dict[str,File] = {}
        self.fields: dict[str, Field] = {}

        def on_field(f: FieldProtocol) -> None:
            self.fields[f.field_name.decode()] = f

        def on_file(f: FileProtocol) -> None:
            self.files[f.field_name.decode()] = f

        def on_end() -> None:
            self.ended = True

        # Get a form-parser instance.
        self.f = FormParser("multipart/form-data", on_field, on_file, on_end, boundary=self.boundary, config=config)

    def parse(self, body: bytes) -> None:
        self.f.write(body)
        self.f.finalize()

@dataclass
class Part:
    name: bytes
    body: bytes

def build_body(boundary: bytes, parts: List[Part]) ->bytes:
    crlf = b'\r\n'
    body = bytearray()
    body += b'--' + boundary
    for p in parts:
        body += crlf
        body += b'Content-Disposition: form-data; name="' + p.name + b'"; filename="' + p.name + b'"' + crlf
        body += crlf
        body += p.body
        body += crlf
        body += b'--' + boundary
    body += b'--' + crlf
    return bytes(body)


def test() -> None:

    test_data: list[Tuple[bytes, bytes]] = [
        #(b'fo' * 300000 + b'\r\n' + b'foobar', "b'fo' * 300000 + b'\\r\\n' + b'foobar',"),
        #(b'fo' * 290000 + b'\r\n' * 10000 + b'foobar',"b'fo' * 290000 + b'\\r\\n' * 10000 + b'foobar'"),
        #(b'fo' * 150000 + b'\r\n' * 150000 + b'foobar',"b'fo' * 150000 + b'\r\n' * 150000 + b'foobar'"),
        #((b'fo' + b'\r\n') * 150000 + b'foobar',"(b'fo' + b'\\r\\n') * 150000 + b'foobar'"),
        #((b'fo' + b'\r\n' * 5) * 50000 + b'foobar',"(b'fo' + b'\\r\\n' * 5) * 50000 + b'foobar'"),
        #((b'fo' + b'\r\n' * 50) * 5000 + b'foobar',"(b'fo' + b'\\r\\n' * 50) * 5000 + b'foobar'"),
        #(b'fo' + b'\r\n' * 300000 + b'foobar',"b'fo' + b'\\r\\n' * 300000 + b'foobar'"),
        (b'fo' + b'oo' * 300000 + b'foobar',"b'fo' + b'oo' * 300000 + b'foobar'"),
        (random.randbytes(600000), 'randbytes(600000)'),
    ]

    def run_it(data, verify=False) -> None:
        boundary = random.randbytes(16).hex().encode()
        part_list =  [ 
            Part(name=b'sample', body=data),
            Part(name=b'foo', body=b'fghj'),
            Part(name=b'sample2', body=data),
            Part(name=b'sample3', body=data),
            Part(name=b'sample4', body=data),
        ]
        body = build_body(boundary,part_list)
        headers = {'Content-Length': f'{len(body)}'.encode(),
                    'Content-Type': b'multipart/form-data; boundary=' + boundary}
        parser = TestFormParser(headers)
        parser.parse(body)
        if (verify):
            for part in part_list:
                fo = parser.files[part.name.decode()].file_object
                fo.seek(0)
                actual_data = fo.read()
                if (actual_data != part.body):
                    print(f'MISMATCH name={part.name} data actual len: {len(actual_data)} expected: {len(part.body)}')

    iters = 1
    times: list[float] = []
    for sample, data_format in test_data:
        sample = sample * 100
        sample_size = len(sample)
        crlf_count = sample.count(b'\r\n')
        run_it(sample, verify=True)
        measurement_time = timeit.timeit(lambda: run_it(sample), setup="pass",number=iters)
        print(f'data format: {data_format}')
        print(f'It took {measurement_time:.3f}s to run {iters} iter with sample size: {sample_size}.')
        print(f'Sample contain {crlf_count} \\r\\n characters.\n\n')
        times.append(measurement_time)

    _min = min(times)
    _max = max(times)
    mean = sum(times) / len(times)
    print(f'Biggest difference is {_max-_min:.2f}s ({_max/_min*100:.2f}%) for sample of the same size, mean: {mean}')

if __name__ == '__main__':
    test()