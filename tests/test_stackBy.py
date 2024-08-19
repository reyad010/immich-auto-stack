from faker import Faker
import pytest
from unittest.mock import ANY

from immich_auto_stack import stackBy


def mock_criteria(x):
    return (x["originalFileName"].split(".")[0], x["localDateTime"])


fake = Faker()


def asset_factory(file_base=None, date_time=None, extension="jpg"):
    file_name = (file_base or fake.unique.file_name(extension="")) + "." + extension
    return {
        "originalFileName": file_name,
        "localDateTime": date_time or fake.unique.date_time(),
    }


@pytest.mark.parametrize(
    "test_base1,test_ext1,test_base2,test_ext2",
    [
        ("test_filename", "raw", "test_filename2", "raw"),
        ("test_Filename", "raw", "test_filename", "raw"),
        ("_", "raw", "__", "raw"),
        ("test_filename", "Jpg", "test_filename2", "Jpg"),
        ("test_filename", "tar.jpg", "test_filename2", "tar.jpg"),
    ],
)
def test_stackBy_creates_two_groups_for_different_filenames(
    test_base1, test_ext1, test_base2, test_ext2
):
    # Arrange
    file1_1 = asset_factory(file_base=test_base1, extension=test_ext1)
    file1_2 = asset_factory(file_base=test_base1, date_time=file1_1["localDateTime"])
    file2_1 = asset_factory(file_base=test_base2, extension=test_ext2)
    file2_2 = asset_factory(file_base=test_base2, date_time=file2_1["localDateTime"])
    expected_result = [
        ((test_base1, file1_1["localDateTime"]), ANY),
        ((test_base2, file2_1["localDateTime"]), ANY),
    ]

    # Act
    result = stackBy(data=[file1_1, file2_1, file1_2, file2_2], criteria=mock_criteria)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "extensions",
    [
        ["raw", "jpg"],
        ["raw", "jpg", "txt", "XMP"],
        ["raw", "png", "_"],
        ["jpg", "5"],
    ],
)
def test_stackBy_creates_list_of_file_assets_within_group(extensions):
    # Arrange
    extensions.sort()
    test_file_base = "test_filename"
    test_date_time = fake.date_time()
    assets = [
        asset_factory(file_base=test_file_base, extension=e, date_time=test_date_time)
        for e in extensions
    ]
    expected_result = [((test_file_base, test_date_time), assets)]

    # Act
    result = stackBy(data=assets, criteria=mock_criteria)

    # Assert
    assert result == expected_result
    assert len(result[0][1]) > 1


def test_stackBy_does_not_group_files_with_same_date_time_but_different_filename():
    # Arrange
    test_date_time = fake.date_time()
    file_1 = asset_factory(date_time=test_date_time)
    file_2 = asset_factory(date_time=test_date_time)
    expected_result = []

    # Act
    result = stackBy(data=[file_1, file_2], criteria=mock_criteria)

    # Assert
    assert result == expected_result


def test_stackBy_does_not_group_files_with_same_filename_but_different_datetime():
    # Arrange
    file_1 = asset_factory(file_base="test_filename", extension="jpg")
    file_2 = asset_factory(file_base="test_filename", extension="raw")
    expected_result = []

    # Act
    result = stackBy(data=[file_1, file_2], criteria=mock_criteria)

    # Assert
    assert result == expected_result