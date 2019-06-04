from re import sub, findall, compile


def __quote__(x):
    if ' ' in x or ',' in x:
        return '\"' + x + '\"'
    else:
        return x


class TemplateParser:

    def __init__(self, template_file, input_file):
        template = open(template_file).read().strip()
        self.regex = template
        for char in '^$()[]*+?{}|':
            self.regex = self.regex.replace(char, '\\' + char)
        self.regex = sub(r'[ \t]+', "[ \t]+", self.regex)
        self.regex = sub(r'[ \t\r]*\.\.\.[ \t\r]*', "[\\W\\S]*?", self.regex)
        self.regex = sub(r'[ \t]*\.\.[ \t]*', ".*", self.regex)
        self.regex = sub(r'(?<!\\)<[a-zA-Z]+[a-zA-Z0-9_-]*>', "(.+)", self.regex) + "\n"

        text_file = open(input_file).read().strip() + '\n'
        self.value_stream = findall(self.regex, text_file)

        self.idents = findall(r'(?<!\\)<([a-zA-Z]+[a-zA-Z0-9_-]*)>', template)

    def into_iter(self, index=0, object_stream=False):
        if index >= len(self.value_stream):
            return
        if not object_stream:
            if len(self.idents) == 1:
                yield self.idents[0], self.value_stream[index]
            else:
                for i in xrange(len(self.idents)):
                    yield self.idents[i], self.value_stream[index][i]
        else:
            for i in xrange(index, len(self.value_stream)):
                yield self.collect_obj(i)

    def to_csv(self, header=True):
        buffer = ""

        # Add header to inputs ex: name,location,type,etc
        if header:
            buffer = ','.join(map(__quote__, self.idents)) + '\n'

        for obj_index in xrange(len(self.value_stream)):
            buffer += ','.join(map(lambda x: __quote__(x[1]), self.into_iter(obj_index))) + '\n'
        return buffer.strip()

    def debug_fields(self):
        if len(self.value_stream) == 0:
            return "No values could be parsed."
        buffer = "First of " + bytes(len(self.value_stream)) + " entries:\n"
        for ident, value in self.into_iter():
            buffer += ident + " = \"" + value + "\"\n"
        return buffer.strip()

    def __str__(self):
        return self.debug_fields()

    def collect_obj(self, index=0):
        class __FieldWrapper:
            def __init__(self, res):
                for ident, value in res:
                    self.__dict__[ident] = value

            def __str__(self):
                buffer = ""
                for key in self.__dict__:
                    buffer += key + " = \"" + self.__dict__[key] + "\"\n"
                return buffer.strip()

        return __FieldWrapper(self.into_iter(index))


class StreamObjective:
    CSV = 0

    def __init__(self): pass


class TemplateStream:

    def __init__(self, template_file, stream_objective, header=True, time_stamp=False):
        template = open(template_file).read().strip()
        self.regex = template
        for char in '^$()[]*+?{}|':
            self.regex = self.regex.replace(char, '\\' + char)
        self.regex = sub(r'[ \t]+', '[ \t]+', bytes(self.regex))
        self.regex = sub(r'[ \t\r]*\.\.\.[ \t\r]*', "[\\W\\S]*?", self.regex)
        self.regex = sub(r'[ \t]*\.\.[ \t]*', ".*", self.regex)
        self.regex = sub(r'(?<!\\)<[a-zA-Z]+[a-zA-Z0-9_-]*>', "(.+)", self.regex) + "\n"
        self.regex = compile(self.regex)

        self.idents = findall(r'(?<!\\)<([a-zA-Z]+[a-zA-Z0-9_-]*)>', template)
        self.stream_objective = stream_objective
        self.buffer = ""

        if time_stamp:
            self.idents.insert(0, 'timestamp')

        if header:
            stdout.write(','.join(map(__quote__, self.idents)) + '\n')

        while True:
            try:
                self.buffer += raw_input() + '\n'
            except EOFError:
                break
            match = self.regex.search(self.buffer)
            if match is not None:
                self.buffer = self.buffer[match.endpos + 1:]

                groups = list(match.groups())

                if time_stamp:
                    from datetime import datetime
                    groups.insert(0, bytes(datetime.now()))

                self.__process__(groups)

    def __process__(self, groups):
        if self.stream_objective == StreamObjective.CSV:
            stdout.write(','.join(map(__quote__, groups)) + '\n')


if __name__ == "__main__":
    from sys import stdout
    import argparse

    parser = argparse.ArgumentParser(description='A script for collecting and plotting data.')
    parser.add_argument('template', metavar='template_file', help='Template to use for parsing input')
    parser.add_argument('input', metavar='input_file', nargs='?', help='Input to parse')
    parser.add_argument('-c', '--csv', action='store_const', const=True, default=False,
                        help='Output the collected data on stdout as a csv file')
    parser.add_argument('-i', '--ident-headers', action='store_const', const=False, default=True,
                        help='Disable the identifier headers should be output')

    args = parser.parse_args()

    if args.input is None:
        if args.csv:
            TemplateStream(args.template, StreamObjective.CSV, header=args.ident_headers, time_stamp=True)
    else:
        if args.csv:
            parser = TemplateParser(args.template, args.input)
            stdout.write(parser.to_csv(header=args.ident_headers))
