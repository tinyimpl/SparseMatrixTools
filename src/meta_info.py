#!/usr/bin/env python3
import argparse
import os
import scipy.io as sio
import scipy.sparse as sparse
import warnings
from plot import MatrixMarketReader, MatlabReader
from beautifultable import BeautifulTable


class MetaInfo:
    def __init__(self, name, format, mtx) -> None:
        isinstance(mtx, sparse.coo_matrix)
        self.name = name
        self.format = format
        self.rows = mtx.shape[0]
        self.cols = mtx.shape[1]
        self.nnz = mtx.nnz
        self.nnz_per_row = mtx.nnz / mtx.shape[0]

    def __header(self):
        return ["name", "format", "rows", "cols", "nnz", "nnz/row"]

    def __body(self):
        return [
            self.name,
            self.format,
            self.rows,
            self.cols,
            self.nnz,
            self.nnz_per_row,
        ]

    def __str__(self) -> str:
        warnings.filterwarnings("ignore")
        table = BeautifulTable()
        table.column_headers = self.__header()
        table.append_row(self.__body())
        warnings.resetwarnings()
        return table.__str__()


class MatrixMarketMetaInfo:
    reader_ = MatrixMarketReader()

    def analysis(self, mtx_format, mtx_path) -> str:
        mtx = self.reader_.read(mtx_path)
        return MetaInfo(mtx_path, mtx_format, mtx).__str__()


class MatlabMetaInfo:
    reader_ = MatlabReader()

    def analysis(self, mtx_format, mtx_path) -> str:
        mtx = self.reader_.read(mtx_path)
        return MetaInfo(mtx_path, mtx_format, mtx).__str__()


class MetaInfoProgram:
    def __init__(self) -> None:
        self.__info_factory = {"mm": MatrixMarketMetaInfo(), "mat": MatlabMetaInfo()}
        self.__mtx_format = ""
        self.__mtx_file = ""
        pass

    def run(self, parser):
        self.__parse_args(parser)
        self.__check_args()
        self.__print()

    def __parse_args(self, parser):
        parser.add_argument(
            "--format",
            help="sparse matrix format",
            type=str,
            required=True,
            choices=self.__info_factory.keys(),
        )
        parser.add_argument(
            "--file", help="sparse matrix file", type=str, required=True
        )
        args = parser.parse_args()
        self.__mtx_format = args.format
        self.__mtx_file = args.file

    def __check_args(self):
        if os.path.isfile(self.__mtx_file) is False:
            raise Exception(
                "sparse matrix file is not exists, matrix file: {}".format(
                    self.__mtx_file
                )
            )
        if self.__mtx_format == "mat":
            warnings.warn(
                "only the matlab-format sparse matrix downloaded form sparse.tamu.edu is supported!!!",
                RuntimeWarning,
            )

    def __read_mtx(self):
        try:
            mtx = self.__reader_factory[self.__mtx_format].read(self.__mtx_file)
        except KeyError:
            raise Exception(
                "unsupported sparse matrix format, sparse matrix format: {}".format(
                    self.__mtx_format
                )
            )
        except Exception:
            raise Exception(
                "illegal matrix, sparse matrix format: {}, sparse matrix file: {}".format(
                    self.__mtx_format, self.__mtx_file
                )
            )
        return mtx

    def __print(self):
        try:
            meta_info = self.__info_factory[self.__mtx_format].analysis(
                self.__mtx_format, self.__mtx_file
            )
        except KeyError:
            raise Exception(
                "unsupported sparse matrix format, sparse matrix format: {}".format(
                    self.__mtx_format
                )
            )
        except Exception:
            raise Exception(
                "illegal matrix, sparse matrix format: {}, sparse matrix file: {}".format(
                    self.__mtx_format, self.__mtx_file
                )
            )
        print(meta_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    MetaInfoProgram().run(parser)
