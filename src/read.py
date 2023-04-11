#!/usr/bin/env python3
import argparse
import os
import warnings
import scipy.io as sio
import scipy.sparse as sparse
from prompt_toolkit import PromptSession, shortcuts
from beautifultable import BeautifulTable
from abc import abstractmethod
from download import ArgumentParser, Command, ExitCommand, ClearCommand
from plot import MatrixMarketReader, MatlabReader
from meta_info import MetaInfo


class ReadProgram:
    def __init__(self) -> None:
        self.mtx = None
        self.meta_info = None

    @abstractmethod
    def set_mtx(self, coo_mtx):
        pass

    @abstractmethod
    def set_meta_info(self, meta_info):
        self.meta_info = meta_info

    @abstractmethod
    def run(self, parser, commands):
        print(self.meta_info)
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


class ReadCommand(Command):
    def __init__(self, subparsers, prog, help_msg, data, lower, upper) -> None:
        super().__init__(subparsers, None)
        self.subparser = subparsers.add_parser(prog, help=help_msg)
        group = self.subparser.add_mutually_exclusive_group()
        group.add_argument("-i", "--index", type=int)
        group.add_argument("-r", "--range", nargs=2, type=int)
        self.data = data
        self.index_lower = lower
        self.index_upper = upper

    def check(self, args):
        if args.range is not None and (
            args.range[0] >= args.range[1]
            or args.range[0] < self.index_lower
            or args.range[1] >= self.index_upper
        ):
            raise Exception()
        if args.index is not None and (
            args.index < self.index_lower or args.index >= self.index_upper
        ):
            raise Exception()

    def run(self, args):
        warnings.filterwarnings("ignore")
        table = BeautifulTable()
        if args.range is not None:
            table.column_header = range(args.range[0], args.range[1])
            table.append_row(self.data[args.range[0] : args.range[1]].tolist())
        if args.index is not None:
            table.colunb_header = ["Row", "Offset"]
            table.append_row([self.data[args.index]])
        warnings.resetwarnings()
        print(table)


class CsrRowOffsetCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(
            subparsers,
            "r",
            "displace csr row offset",
            csr_mtx.indptr,
            0,
            meta_info.rows,
        )


class CsrColIndexCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(
            subparsers,
            "c",
            "displace csr col index",
            csr_mtx.indices,
            0,
            meta_info.nnz,
        )


class CsrValueCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(
            subparsers, "v", "displace values", csr_mtx.data, 0, meta_info.nnz
        )


class ReadCsrProgram(ReadProgram):
    def set_mtx(self, coo_mtx):
        self.mtx = coo_mtx.tocsr()

    def run(self):
        parser = ArgumentParser("CSR Format Read Program")
        subparsers = parser.add_subparsers()
        commands = {
            "r": CsrRowOffsetCommand(subparsers, self.mtx, self.meta_info),
            "c": CsrColIndexCommand(subparsers, self.mtx, self.meta_info),
            "v": CsrValueCommand(subparsers, self.mtx, self.meta_info),
            "exit": ExitCommand(subparsers, None),
            "clear": ClearCommand(subparsers, None),
        }
        super().run(parser, commands)


class CooRowCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(subparsers, "r", "displace row", csr_mtx.row, 0, meta_info.nnz)


class CooColCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(subparsers, "c", "displace col", csr_mtx.col, 0, meta_info.nnz)


class CooValCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(
            subparsers, "v", "displace value", csr_mtx.data, 0, meta_info.nnz
        )


class ReadCooProgram(ReadProgram):
    def set_mtx(self, coo_mtx):
        self.mtx = coo_mtx

    def run(self):
        parser = ArgumentParser("COO Format Read Program")
        subparsers = parser.add_subparsers()
        commands = {
            "r": CooRowCommand(subparsers, self.mtx, self.meta_info),
            "c": CooColCommand(subparsers, self.mtx, self.meta_info),
            "v": CooValCommand(subparsers, self.mtx, self.meta_info),
            "exit": ExitCommand(subparsers, None),
            "clear": ClearCommand(subparsers, None),
        }
        super().run(parser, commands)


class CscRowCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(
            subparsers, "r", "displace row index", csr_mtx.indices, 0, meta_info.nnz
        )


class CscColCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(
            subparsers, "c", "displace col offset", csr_mtx.indptr, 0, meta_info.cols
        )


class CscValCommand(ReadCommand):
    def __init__(self, subparsers, csr_mtx, meta_info) -> None:
        super().__init__(
            subparsers, "v", "displace value", csr_mtx.data, 0, meta_info.nnz
        )


class ReadCscProgram(ReadProgram):
    def set_mtx(self, coo_mtx):
        self.mtx = coo_mtx.tocsc()

    def run(self):
        parser = ArgumentParser("COO Format Read Program")
        subparsers = parser.add_subparsers()
        commands = {
            "r": CscRowCommand(subparsers, self.mtx, self.meta_info),
            "c": CscColCommand(subparsers, self.mtx, self.meta_info),
            "v": CscValCommand(subparsers, self.mtx, self.meta_info),
            "exit": ExitCommand(subparsers, None),
            "clear": ClearCommand(subparsers, None),
        }
        super().run(parser, commands)


if __name__ == "__main__":
    parser = ArgumentParser(prog="Matrix Market Read Program")
    read_factory = {"mm": MatrixMarketReader(), "mat": MatlabReader()}
    as_factory = {
        "csr": ReadCsrProgram(),
        "coo": ReadCooProgram(),
        "csc": ReadCscProgram(),
    }
    parser.add_argument(
        "--format",
        help="input sparse matrix format",
        type=str,
        required=True,
        choices=read_factory.keys(),
    )
    parser.add_argument("--file", help="sparse matrx file", type=str, required=True)
    parser.add_argument(
        "--to", help="read format", type=str, required=True, choices=as_factory.keys()
    )
    try:
        args = parser.parse_args()
    except Exception:
        parser.print_help()
        exit()
    try:
        coo_mtx = read_factory[args.format].read(args.file)
    except KeyError:
        raise Exception(
            "unsupported sparse matrix format, sparse matrix format: {}".format(
                args.format
            )
        )
    except Exception:
        raise Exception(
            "illegal matrix, sparse matrix format: {}, sparse matrix file: {}".format(
                args.format, args.file
            )
        )
    meta_info = MetaInfo(args.file, args.format, coo_mtx)
    as_factory[args.to].set_mtx(coo_mtx)
    as_factory[args.to].set_meta_info(meta_info)
    as_factory[args.to].run()
