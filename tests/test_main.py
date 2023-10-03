import pytest

from ivelum_test_task.main import _modify_body, WORD_BORDERS


class TestModifyBody:
    @pytest.mark.parametrize(
        "original_body,expected_body",
        [
            (">aaaaaa", ">aaaaaa™"),
            ("><aaaaaa", "><aaaaaa"),
            *[(f">aaaaaa™{we}", f">aaaaaa™{we}") for we in WORD_BORDERS],
            ("><aaaaaa>bbbbbb", "><aaaaaa>bbbbbb™"),
            (
                """>The visual description of the colliding files, at
http://shattered.io/static/pdf_format.png, is not very helpful
in understanding how they produced the PDFs, so I took apart
the PDFs and worked it out.

Basically, each PDF contains a single large (421,385-byte) JPG
image, followed by a few PDF commands to display the JPG. The
collision lives entirely in the JPG data - the PDF format is
merely incidental here. Extracting out the two images shows two
JPG files with different contents (but different SHA-1 hashes
since the necessary prefix is missing). Each PDF consists of a
common prefix (which contains the PDF header, JPG stream
descriptor and some JPG headers), and a common suffix (containing
image data and PDF display commands).""",
                """>The visual™ description of the colliding files, at
http://shattered.io/static/pdf_format.png, is not very helpful
in understanding how they produced the PDFs, so I took apart
the PDFs and worked™ it out.

Basically, each PDF contains a single™ large (421,385-byte) JPG
image, followed by a few PDF commands to display the JPG. The
collision lives entirely in the JPG data - the PDF format™ is
merely™ incidental here. Extracting out the two images™ shows two
JPG files with different contents (but different SHA-1 hashes™
since the necessary prefix™ is missing). Each PDF consists of a
common™ prefix™ (which contains the PDF header™, JPG stream™
descriptor and some JPG headers), and a common™ suffix™ (containing
image data and PDF display commands).""",
            ),
            (
                '<a href="http://shattered.io/static/pdf_format.png" rel="nofollow">http://shattered.io/static/pdf_format.png</a>',
                '<a href="http://shattered.io/static/pdf_format.png" rel="nofollow">http://shattered.io/static/pdf_format.png</a>',
            ),
            (
                ">tered.io&#x2F;static&#x2F;pdf_format.pn",
                ">tered.io&#x2F;static&#x2F;pdf_format.pn",
            ),
        ],
        ids=[
            "tag_opened",
            "tag_closed",
            *[f"tag_opened_and_ends_with_{we}" for we in WORD_BORDERS],
            "tag_closed_and_opened",
            "client_test_case",
            "linked_tag",
            "non_visible_symbols",
        ],
    )
    def test_ok(self, original_body, expected_body):
        modified_body = _modify_body(original_body)

        assert modified_body == expected_body
