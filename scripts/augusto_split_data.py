"""Splits the rapgen data"""
import os

from Bio import SeqIO
from Bio.Seq import Seq

import logging

import click
from pathlib import Path

from raptgen.data import AugustoDataSplitter

dir_path = os.path.dirname(os.path.realpath(__file__))
default_path = str(Path(f"{dir_path}/../out/real").resolve())


@click.command(help='run experiment with real data',
               context_settings=dict(show_default=True))
@click.argument("seqpath", type=click.Path(exists=True))
@click.option("--save-dir",
              help="path to save results",
              type=click.Path(),
              default=default_path)
@click.option("--fwd", help="forward adapter", type=str, default=None)
@click.option("--rev", help="reverse adapter", type=str, default=None)
@click.option("--min-count",
              help="minimum duplication count to pass sequence for training",
              type=int,
              default=1)
@click.option("--use-cuda/--no-cuda",
              help="use cuda if available",
              is_flag=True,
              default=True)
def main(seqpath, save_dir, fwd, rev, min_count, use_cuda):
    logger = logging.getLogger(__name__)

    logger.info(f"saving to {save_dir}")
    save_dir = Path(save_dir).expanduser()
    save_dir.mkdir(exist_ok=True, parents=True)

    experiment = AugustoDataSplitter(path=seqpath,
                                     forward_adapter=fwd,
                                     reverse_adapter=rev)

    seqs = experiment.get_dataloader(min_count=min_count, use_cuda=use_cuda)
    print(seqpath)
    print(os.path.basename(seqpath))
    records = []
    for i, seq in enumerate(seqs):
        record = SeqIO.SeqRecord(Seq(seq), id=f'seq{i+1}')
        records.append(record)
    filename = os.path.join(
        save_dir,
        os.path.splitext(os.path.basename(seqpath))[0] + '_filtered.fasta')
    with open(filename, 'w') as handle:
        SeqIO.write(records, handle, 'fasta')


if __name__ == "__main__":
    Path("./.log").mkdir(parents=True, exist_ok=True)
    formatter = '%(levelname)s : %(name)s : %(asctime)s : %(message)s'
    logging.basicConfig(filename='.log/logger.log',
                        level=logging.DEBUG,
                        format=formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
    main()
