#!/usr/bin/env python3
import argparse
import os
import scipy.io as sio
import scipy.sparse as sparse
import numpy as np
from matplotlib.pyplot import figure, show, title


# basic class
class SparseMatrixReader:
    def read(self, mtx_path):
        pass


class MatrixMarketReader(SparseMatrixReader):
    def read(self, mtx_path):
        return sio.mmread(mtx_path)


class PlotProgram:
    __mtx_format = ""
    __mtx_file = ""

    def __init__(self) -> None:
        self.__reader_factory = {
            "mm": MatrixMarketReader(),
        }
        pass

    def run(self, parser):
        self.__parse_args(parser)
        self.__check_args()
        mtx = self.__read_mtx()
        self.__plot(mtx)

    def __parse_args(self, parser):
        parser.add_argument(
            "--format",
            help="sparse matrix format",
            type=str,
            required=True,
            choices=self.__reader_factory.keys(),
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

    def __plot(self, mtx):
        assert isinstance(mtx, sparse.coo_matrix)
        fig = figure()
        ax1 = fig.add_subplot()
        ax1.spy(mtx, markersize=1)
        title(self.__mtx_file)
        show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    PlotProgram().run(parser)
