#!/usr/bin/env python3
import argparse
import ssgetpy as ssget
import warnings
from os import path
from prompt_toolkit import PromptSession, shortcuts
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
        raise Exception


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
        self.subparser.add_argument(
            "-r", "--rowbounds", nargs=2, type=int, default=None
        )
        self.subparser.add_argument(
            "-c", "--colbounds", nargs=2, type=int, default=None
        )
        self.subparser.add_argument("-n", "--nzbounds", nargs=2, type=int, default=None)
        self.subparser.add_argument("--isspd", type=bool, default=None)
        self.subparser.add_argument("--is2d3d", type=bool, default=None)
        self.subparser.add_argument(
            "-d",
            "--dtype",
            type=str,
            default=None,
            choices=["real", "complex", "binary"],
        )
        self.subparser.add_argument("-g", "--group", type=str, default=None)
        self.subparser.add_argument("-k", "--kind", type=str, default=None)
        self.subparser.add_argument("-l", "--limit", type=int, default=10)

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
            self.states.mtx_cache.add_item(mtx)


class DownloadCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("download", help="downalod matrix")
        self.subparser.add_argument(
            "-f",
            "--format",
            type=str,
            required=False,
            choices=["mm", "rb", "mat"],
            default="mm",
        )
        self.subparser.add_argument(
            "-e", "--extract", required=False, type=bool, default=False
        )
        self.subparser.add_argument(
            "-d", "--dest", required=False, type=str, default=path.curdir
        )

    def check(self, args):
        if path is not None and not path.exists(args.dest):
            raise Exception("dest path is not exist!!!")

    def run(self, args):
        if len(self.states.mtx_cart) == 0:
            warnings.warn(
                "matrix cart is empty!!!",
                RuntimeWarning,
            )
            return
        for mtx in self.states.mtx_cart.values():
            mtx.download(
                format=args.format.upper(), extract=args.extract, destpath=args.dest
            )
        self.states.mtx_cart.clear()


class CacheCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("cache", help="show matrix cache")

    def check(self, args):
        pass

    def run(self, args):
        if len(self.states.mtx_cache) == 0:
            warnings.warn(
                "matrix cache is empty!!!",
                RuntimeWarning,
            )
            return
        print_mtxs(self.states.mtx_cache.values())


class ListCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("list", help="list matrix cart")

    def check(self, args):
        pass

    def run(self, args):
        if len(self.states.mtx_cart) == 0:
            warnings.warn(
                "matrix cart is empty!!!",
                RuntimeWarning,
            )
            return
        print_mtxs(self.states.mtx_cart.values())


class AddCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("add", help="add matrix to cart")
        group = self.subparser.add_mutually_exclusive_group()
        group.add_argument("-i", "--id", type=int)
        group.add_argument("-n", "--name", type=str)

    def check(self, args):
        pass

    def run(self, args):
        try:
            if args.id is not None:
                mtx = self.states.mtx_cache.get_item_by_id(args.id)
            if args.name is not None:
                mtx = self.states.mtx_cache.get_item_by_name(args.name)
        except:
            warnings.warn("input is not in cache!!!")
            return
        self.states.mtx_cart.add_item(mtx)


class RemoveCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("remove", help="remove matrix in cart")
        group = self.subparser.add_mutually_exclusive_group()
        group.add_argument("-i", "--id", type=int)
        group.add_argument("-n", "--name", type=str)

    def check(self, args):
        pass

    def run(self, args):
        if args.id is not None:
            self.states.mtx_cart.remove_item_by_id(args.id)
        if args.name is not None:
            self.states.mtx_cart.remove_item_by_name(args.name)


class ClearCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("clear", help="clear screen")

    def check(self, args):
        pass

    def run(self, args):
        shortcuts.clear()


class ExitCommand(Command):
    def __init__(self, subparsers, states) -> None:
        super().__init__(subparsers, states)
        self.subparser = subparsers.add_parser("exit", help="exit program")

    def check(self, args):
        pass

    def run(self, args):
        exit()


class MtxMap:
    def __init__(self) -> None:
        self.__id_to_mtx_map = dict()
        self.__name_to_mtx_map = dict()

    def add_item(self, mtx):
        if mtx is not None:
            self.__id_to_mtx_map[mtx.id] = mtx
            self.__name_to_mtx_map[mtx.name] = mtx

    def remove_item_by_id(self, id):
        if id is not None:
            try:
                name = self.__id_to_mtx_map[id].name
                del self.__id_to_mtx_map[id]
                del self.__name_to_mtx_map[name]
            except:
                pass

    def remove_item_by_name(self, name):
        if name is not None:
            try:
                id = self.__name_to_mtx_map[name].id
                del self.__name_to_mtx_map[name]
                del self.__id_to_mtx_map[id]
            except:
                pass

    def get_item_by_id(self, id):
        return self.__id_to_mtx_map[id]

    def get_item_by_name(self, name):
        return self.__name_to_mtx_map[name]

    def values(self):
        return self.__id_to_mtx_map.values()

    def clear(self):
        self.__id_to_mtx_map.clear()
        self.__name_to_mtx_map.clear()

    def __len__(self):
        assert len(self.__id_to_mtx_map) == len(self.__name_to_mtx_map)
        return len(self.__id_to_mtx_map)


class State:
    mtx_cache = MtxMap()
    mtx_cart = MtxMap()


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
            "add": AddCommand(subparsers, state),
            "remove": RemoveCommand(subparsers, state),
            "clear": ClearCommand(subparsers, state),
            "exit": ExitCommand(subparsers, state),
        }
        session = PromptSession()
        while 1:
            input = session.prompt(">> ").lower()
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
