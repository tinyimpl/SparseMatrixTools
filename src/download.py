#!/usr/bin/env python3
import argparse
import ssgetpy as ssget
import warnings
from prompt_toolkit import prompt
from beautifultable import BeautifulTable
from abc import abstractmethod


def print_mtxs(mtxs):
    mtxs = list(mtxs)
    if mtxs is not None and len(mtxs) != 0:
        warnings.filterwarnings("ignore")
        table = BeautifulTable()
        table.column_headers = mtxs[0].attr_list[0:-4]
        for mtx in mtxs:
            table.append_row(mtx.to_tuple()[0:-4])
        warnings.resetwarnings()
        print(table)
    else:
        print()


class ArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        raise Exception()


class Command:
    @abstractmethod
    def __init__(self, subparsers, states) -> None:
        self.subparser = None
        self.states = states
        pass

    def exec(self, parser, input):
        try:
            args = self.parser(parser, input)
            self.check(args)
        except Exception:
            self.print_help()
            return
        self.run(args)

    def print_help(self):
        self.subparser.print_help()

    def parser(self, parser, input):
        return parser.parse_args(input)

    @abstractmethod
    def check(self, args):
        pass

    @abstractmethod
    def run(self, args):
        pass


class SearchCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("search", help="search sparse matrix")
        self.subparser.add_argument("--rowbounds", type=tuple, default=(None, None))
        self.subparser.add_argument("--colbounds", type=tuple, default=(None, None))
        self.subparser.add_argument("--nzbounds", type=tuple, default=(None, None))
        self.subparser.add_argument("--isspd", type=bool, default=None)
        self.subparser.add_argument("--is2d3d", type=bool, default=None)
        self.subparser.add_argument(
            "--dtype", type=str, default=None, choices=["real", "complex", "binary"]
        )
        self.subparser.add_argument("--group", type=str, default=None)
        self.subparser.add_argument("--kind", type=str, default=None)
        self.subparser.add_argument("--limit", type=int, default=10)

    def run(self, args):
        mtxs = ssget.search(
            rowbounds=args.rowbounds,
            colbounds=args.colbounds,
            nzbounds=args.nzbounds,
            isspd=args.isspd,
            is2d3d=args.is2d3d,
            dtype=args.dtype,
            group=args.group,
            kind=args.kind,
            limit=args.limit,
        )
        print_mtxs(mtxs)
        for mtx in mtxs:
            self.states.mtx_cache.add(mtx)


class DownloadCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("download", help="downalod matrix")
        self.subparser.add_argument(
            "--format",
            type=str,
            required=False,
            choices=["mm", "rb", "mat"],
            default="mm",
        )
        self.subparser.add_argument(
            "--extract", required=False, type=bool, default=False
        )

    def check(self, args):
        pass

    def run(self, args):
        if self.states.mtx_cart is None or len(self.states.mtx_cart) == 0:
            warnings.warn(
                "matrix cart is empty!!!",
                RuntimeWarning,
            )
            return
        for mtx in self.states.mtx_cart:
            mtx.download(format=args.format.upper(), extract=args.extract)
        self.states.mtx_cart.clear()


class CacheCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("cache", help="show matrix cache")

    def check(self, args):
        pass

    def run(self, args):
        if self.states.mtx_cache is None or len(self.states.mtx_cache) == 0:
            warnings.warn(
                "matrix cache is empty!!!",
                RuntimeWarning,
            )
            return
        print_mtxs(self.states.mtx_cache)


class ListCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("list", help="list matrix cart")

    def check(self, args):
        pass

    def run(self, args):
        if self.states.mtx_cart is None or len(self.states.mtx_cart) == 0:
            warnings.warn(
                "matrix cart is empty!!!",
                RuntimeWarning,
            )
            return
        print_mtxs(self.states.mtx_cart)


class AppendCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("append", help="append matrix to cart")
        group = self.subparser.add_mutually_exclusive_group()
        group.add_argument("--id", type=int)
        group.add_argument("--name", type=str)

    def check(self, args):
        pass

    def run(self, args):
        for mtx in self.states.mtx_cache:
            if args.id is None and args.name == mtx.name:
                self.states.mtx_cart.add(mtx)
            if args.name is None and args.id == mtx.id:
                self.states.mtx_cart.add(mtx)


class RemoveCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("remove", help="remove matrix in cart")
        group = self.subparser.add_mutually_exclusive_group()
        group.add_argument("--id", type=int)
        group.add_argument("--name", type=str)

    def check(self, args):
        pass

    def run(self, args):
        for mtx in self.states.mtx_cart:
            if args.id is None and args.name == mtx.name:
                self.states.mtx_cart.remove(mtx)
                return
            if args.name is None and args.id == mtx.id:
                self.states.mtx_cart.remove(mtx)
                return


class ExitCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("exit", help="exit program")

    def check(self, args):
        pass

    def run(self, args):
        exit()


class State:
    mtx_cache = set()
    mtx_cart = set()


class DownloadProgram:
    def run(self):
        state = State()
        parser = ArgumentParser(prog="Matrix Market Download Program")
        subparsers = parser.add_subparsers()
        commands = {
            "search": SearchCommand(subparsers, state),
            "download": DownloadCommand(subparsers, state),
            "list": ListCommand(subparsers, state),
            "cache": CacheCommand(subparsers, state),
            "append": AppendCommand(subparsers, state),
            "remove": RemoveCommand(subparsers, state),
            "exit": ExitCommand(subparsers, state),
        }
        while 1:
            input = prompt(">").lower()
            if len(input) > 0:
                try:
                    input = input.split()
                    commands[input[0]].exec(parser, input)
                except KeyError:
                    parser.print_help()
            else:
                parser.print_help()


if __name__ == "__main__":
    DownloadProgram().run()
