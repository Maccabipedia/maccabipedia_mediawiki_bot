from pathlib import Path


_logger = logging.getLogger(__name__)

def upload_single_paper(paper_file_path: Path):
    pass

def upload_papers(papers_directory: Path):
    for paper_file_path in (_ for _ in papers_directory.iterdir() if _.is_file()):
        try:
            upload_single_paper(paper_file_path)
        except Exception
        pass


if __name__ == "__main__":
    PAPERS_DIRECTORY = Path(r'C:\code\maccabipedia_papers_to_upload')
    upload_papers(PAPERS_DIRECTORY)