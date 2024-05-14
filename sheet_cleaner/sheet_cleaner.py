import argparse
import logging
import re
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M')
logger = logging.getLogger(__name__)


class SheetCleaner:
    subs_rules_txt = [
        (r"<span[\r\n\s]+style='mso-spacerun:yes'>&nbsp;</span>", r"<span style='color:white;'>&nbsp;</span>"),
        (r"<o:p></o:p>", '')
    ]
    subs_rules_re = [(re.compile(rule[0]), rule[1]) for rule in subs_rules_txt]

    @classmethod
    def clean_html(cls, src_content):
        dst_content = src_content
        for rule in cls.subs_rules_re:
            dst_content = rule[0].sub(rule[1], dst_content)
        return dst_content

    @classmethod
    def clean_file(cls, src_file: Path, dst_file: Path):
        with src_file.open('rt') as fp:
            src_content = fp.read()
        dst_content = cls.clean_html(src_content)
        with dst_file.open('wt') as fp:
            fp.write(dst_content)

    @classmethod
    def clean_dir(cls, src_dir: Path, dst_dir: Path):
        cls._clean_dir(src_dir=src_dir,
                       dst_dir=dst_dir,
                       curr_dir=src_dir)

    @classmethod
    def _clean_dir(cls, src_dir: Path, dst_dir: Path, curr_dir: Path):
        suffixes = ('.html', '.htm')
        for child in curr_dir.iterdir():
            if child.is_file():
                if child.suffix.lower() in suffixes:
                    cls.clean_file(src_file=child,
                                   dst_file=dst_dir / child.relative_to(src_dir))
            elif child.is_dir():
                cls._clean_dir(src_dir=src_dir,
                               dst_dir=dst_dir,
                               curr_dir=child)


class PathType:
    def __init__(self, is_file=False, is_dir=False, readable=False, nullable=False):
        self.is_file = is_file
        self.is_dir = is_dir
        self.readable = readable
        self.nullable = nullable

    def __call__(self, raw: str) -> Optional[Path]:
        if not raw and self.nullable:
            return None

        p = Path(raw)
        if self.readable and not p.exists():
            raise argparse.ArgumentTypeError(f'Path {raw} does not exist')
        if p.exists():
            if self.is_file and not p.is_file():
                raise argparse.ArgumentTypeError(f'Path {raw} is not a file')
            if self.is_dir and not p.is_dir():
                raise argparse.ArgumentTypeError(f'Path {raw} is not a directory')
        return p

def main():
    parser = argparse.ArgumentParser(description='Sheet HTML Cleaner')
    parser.add_argument('--src-file', '--src_file', type=PathType(is_file=True, readable=True),
                        help='source html file to clean')
    parser.add_argument('--dst-file', '--dst_file', type=PathType(is_file=True),
                        help='dest html file to output (default: source file appended with "-new"')
    parser.add_argument('--src-dir', '--src_dir', type=PathType(is_dir=True, readable=True),
                        help='source html file dir to clean')
    parser.add_argument('--dst-dir', '--dst_dir', type=PathType(is_dir=True),
                        help='dest html file dir to clean (default: source dir appended with "-new")')
    args = parser.parse_args()

    def get_default_dst(src_file: Path) -> Path:
        pos = src_file.name.find('.')
        if pos >= 0:
            fname = src_file.name[:pos] + '-new' + src_file.name[pos:]
        else:
            fname = src_file.name + '-new'
        return src_file.parent / fname

    if args.src_file:
        if not args.dst_file:
            args.dst_file = get_default_dst(args.src_file)
        logger.info('src file: %s', str(args.src_file))
        logger.info('dst file: %s', str(args.dst_file))
        SheetCleaner.clean_file(args.src_file, args.dst_file)
    if args.src_dir:
        if not args.dst_dir:
            args.dst_dir = get_default_dst(args.src_dir)
        logger.info('src dir: %s', str(args.src_dir))
        logger.info('dst dir: %s', str(args.dst_dir))
        SheetCleaner.clean_dir(args.src_dir, args.dst_dir)

if __name__ == '__main__':
    main()
