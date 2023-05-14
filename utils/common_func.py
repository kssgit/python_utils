import requests
import traceback
import json
import os
import csv
import hashlib
import shutil

from pathlib import Path
from enum import Enum
from typing import Union, Tuple, Any, List
from dataclasses import dataclass


COMMON_TIMEOUT = 2


class RequestMethods(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"


def common_request(
    ip: str,
    port: int,
    path: str = "",
    timeout: int = COMMON_TIMEOUT,
    protocol: str = "http",
    headers: dict = {},
    params: dict = {},
    method: RequestMethods = RequestMethods.GET,
) -> Tuple[Any, bool, str]:
    """
    Description: request method 유형에 따라 request를 보내는 함수

    Args:
        ip (str): request ip
        port (int): request port
        path (str, optional): request path. Defaults to "".
        timeout (int, optional): request timeout. Defaults to COMMON_TIMEOUT.
        headers (dict, optional): request header. Defaults to {}.
        params (dict, optional): request parameter. Defaults to {}.
        method (RequestMethods, optional): request method type. Defaults to "RequestMethods.GET".

    Returns:
        Tuple[Any, bool, str]: (request 결과 값, request 성공 여부, message)
    """
    res = None
    is_success = False
    message = ""
    try:
        url = "{}://{}:{}/{}".format(protocol, ip, port, path)
        match method:
            case RequestMethods.GET:
                result = requests.get(
                    url, timeout=timeout, headers=headers, params=params
                )
            case RequestMethods.POST:
                result = requests.post(
                    url, timeout=timeout, headers=headers, json=params
                )
            case RequestMethods.DELETE:
                result = requests.delete(
                    url, timeout=timeout, headers=headers, json=params
                )
            case RequestMethods.PUT:
                result = requests.put(
                    url, timeout=timeout, headers=headers, json=params
                )
            case _:
                raise Exception("Do not support request method")
        if result.status_code == requests.codes.ok:
            res = result.json()["result"]
            is_success = True
    except requests.exceptions.ConnectionError as rece:
        message = str(rece)
        traceback.print_exc()
    except ConnectionRefusedError as cre:
        message = str(cre)
        traceback.print_exc()
    except requests.exceptions.ReadTimeout as rert:
        message = str(rert)
        traceback.print_exc()
    except Exception as e:
        message = str(e)
        traceback.print_exc()
    return (res, is_success, message)


class MemoryUnit(Enum):
    B = 0
    kB = 1
    MB = 2
    GB = 3
    TB = 4
    PB = 5
    KiB = 6
    MiB = 7
    GiB = 8
    TiB = 9
    PiB = 10


def convert_bytes(
    size: Union[float, int], target_unit: MemoryUnit, return_num: bool = True
) -> Union[float, str]:
    """
    Description: byte -> KB, MB, GB, TB, PB, KiB, MiB, GiB, TiB, PiB로 변환 시켜주는 함수

    Args:
        size (float): 변환 시키려는 byte 크기
        target_unit (MemoryUnit, optional): 변환 시키려는 단위. Defaults to MemoryUnit.KB.
        return_num (bool, optional): 단위 없이 숫자만 결과값으로 반환. Defaults to False.

    Returns:
        float: KB, MB, GB, TB, PB, KiB, MiB, GiB, TiB, PiB
    """
    if not isinstance(size, (float, int)):
        raise ValueError("Size type is not valid")
    if target_unit.value < 6:
        size /= 1000**target_unit.value
    else:
        size /= 1024 ** (target_unit.value - 5)
    if return_num:
        return size
    return f"{size:.2f} {target_unit.name}"


def convert_to_bytes(
    size: Union[float, int], target_unit: MemoryUnit, return_num: bool = True
) -> Union[float, str]:
    """
    Description: KB, MB, GB, TB, PB, KiB, MiB, GiB, TiB, PiB -> byte로 변환 시켜주는 함수

    Args:
        size (float): 변환 시키려는 크기
        target_unit (MemoryUnit, optional): 변환 시키려고 하는 사이즈의 단위. Defaults to MemoryUnit.KB.
        return_num (bool, optional): 단위 없이 숫자만 결과값으로 반환. Defaults to False.

    Returns:
        float: B(byte)
    """
    if not isinstance(size, (float, int)):
        raise ValueError("Size type is not valid")
    if target_unit.value < 6:
        size *= 1000**target_unit.value
    else:
        size *= 1024 ** (target_unit.value - 6)
    if return_num:
        return size
    return f"{size:.2f} {MemoryUnit.B.name}"


def convert_data_size(
    size: Union[float, int],
    current_unit: MemoryUnit,
    convert_unit: MemoryUnit,
    return_num: bool = True,
) -> Union[float, str]:
    """
    Description: 데이터 크기 단위 변환 함수

    Args:
        size (float): 변환 시키려는 데이터 크기
        current_unit (MemoryUnit): 현재 데이터 크기의 단위
        convert_unit (MemoryUnit): 변환하고자 하는 데이터 크기의 단위
        return_num (bool, optional): 단위 없이 숫자만 결과값으로 반환. Defaults to False.

    Returns:
        Union[float, str]: 변환된 데이터 크기
    """
    size_in_bytes = convert_to_bytes(size, current_unit, True)
    return convert_bytes(size_in_bytes, convert_unit, return_num)


class ExtensionType(Enum):
    TXT = ".txt"
    JSON = ".json"
    CSV = ".csv"
    LOG = ".log"
    PY = ".py"


def read_json(file_path: Union[str, Path], chunk_size: int = 0) -> Union[list, dict]:
    """
    Description: Json 파일의 내용을 읽어오기 위한 함수

    Args:
        file_path (Union[str, Path]): 파일 경로
        chunk_size (int, optional): 파일이 클 경우 chunk 단위로 나눠 읽어오기위한 파라미터. Defaults to 0.

    Raises:
        FileNotFoundError: 해당 파일 경로에 파일이 없을 경우 발생
        json.JSONDecodeError: json 형태가 아니거나 불완전한 json data일 경우 발생

    Returns:
        Union[list, dict]
    """
    try:
        with open(file_path, "r") as f:
            if chunk_size == 0:
                return json.load(f)
            return json.load("".join(iter(lambda: f.read(chunk_size), "")))
    except FileNotFoundError as e:
        raise Exception(f"file not found error : {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"json decode error : {str(e)}")


def read_file(
    file_path: Union[str, Path], read_line_by_line: bool = False, chunk_size: int = 0
) -> Union[List[str], str]:
    """
    Description: 일반 파일의 내용을 읽어오기 위한 함수

    Args:
        file_path (Union[str, Path]): 파일 경로
        read_line_by_line (bool, optional): 한줄 씩 읽어서 list에 담을 것인지 정하기 위한 트리거 파라미터. Defaults to False.
        chunk_size (int, optional): 파일이 클 경우 chunk 단위로 나눠 읽어오기위한 파라미터. Defaults to 0.

    Raises:
        FileNotFoundError: 해당 파일 경로에 파일이 없을 경우 발생

    Returns:
        Union[List[str], str]
    """
    try:
        with open(file_path, "r") as f:
            if read_line_by_line:
                if chunk_size == 0:
                    return f.read().splitlines()
                return "".join(iter(lambda: f.read(chunk_size), "")).splitlines()
            if chunk_size == 0:
                return f.read()
            return "".join(iter(lambda: f.read(chunk_size), ""))
    except FileNotFoundError as e:
        raise Exception(f"file not found error : {str(e)}")


def read_csv(
    file_path: Union[str, Path], chunk_size: int = 1000, has_header: bool = False
) -> list:
    """
    Description: csv 파일의 내용을 읽어오기 위한 함수

    Args:
        file_path (Union[str, Path]): 파일 경로
        chunk_size (int, optional): 파일이 클 경우 chunk 단위로 나눠 읽어오기위한 파라미터. Defaults to 1000.
        has_header (bool, optional): csv 파일의 header 값을 받아올 것인지 정하기 위한 트리거 파라미터. Defaults to False.

    Raises:
        FileNotFoundError: 해당 파일 경로에 파일이 없을 경우 발생

    Returns:
        list:
    """
    data: List[list] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            if has_header:
                header = next(reader)
            for i, row in enumerate(reader):
                if i % chunk_size == 0:
                    data.append([])
                data[-1].append(row)
        if has_header:
            data.insert(0, header)
        return data
    except FileNotFoundError as e:
        raise Exception(f"file not found error : {str(e)}")


def write_json(
    file_path: Union[str, Path], data: Union[dict, List[dict]], mode: str = "w"
) -> bool:
    """
    Description: json 파일의 내용을 쓰기위한 함수

    Args:
        file_path (Union[str, Path]): 파일 경로
        data (Union[dict, List[dict]]): 저장하기위한 데이터
        mode (str, optional): 쓰기 모드 (a: 이어쓰기, w: 덮어쓰기 ). Defaults to "w".

    Raises:
        FileNotFoundError: 해당 파일 경로에 파일이 없을 경우 발생

    Returns:
        bool: 쓰기 성공 시 True, 실패 시 False
    """
    mode = "w" if mode not in ["a", "w"] else mode
    try:
        with open(file_path, mode) as f:
            json.dump(data, f)
        return True
    except FileNotFoundError as e:
        return False
    except Exception as e:
        traceback.print_exc()
        return False


# TODO
# 바이너리, __str__()이 정의하지 않은 객체, 모듈, 함수등이 data로 들어올 경우를 대비해야 하나?
def write_file(file_path: Union[str, Path], data: str, mode: str = "w") -> bool:
    """
    Description: 일반 파일의 내용을 쓰기위한 함수 (log, txt, py)

    Args:
        file_path (Union[str, Path]): 파일 경로
        data (str, optional): 저장하기위한 데이터
        mode (str, optional): 쓰기 모드 (a: 이어쓰기, w: 덮어쓰기 ). Defaults to "w".

    Raises:
        FileNotFoundError: 해당 파일 경로에 파일이 없을 경우 발생

    Returns:
        bool: 쓰기 성공 시 True, 실패 시 False
    """
    if not isinstance(data, str):
        data = str(data)
    mode = "w" if mode not in ["a", "w"] else mode
    try:
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(data)
        return True
    except FileNotFoundError as e:
        return False
    except Exception as e:
        return False


def write_csv(
    file_path: Union[str, Path], data: List[List[str]], mode: str = "w"
) -> bool:
    """
    Description: csv 파일의 내용을 쓰기위한 함수

    Args:
        file_path (Union[str, Path]): 파일 경로
        data (List[List[str]], optional): 저장하기위한 데이터
        mode (str, optional): 쓰기 모드 (a: 이어쓰기, w: 덮어쓰기 ). Defaults to "w".

    Raises:
        FileNotFoundError: 해당 파일 경로에 파일이 없을 경우 발생

    Returns:
        bool: 쓰기 성공 시 True, 실패 시 False
    """
    mode = mode if mode in ["a", "w"] else "w"
    try:
        with open(file_path, mode, encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(data)
        return True
    except FileNotFoundError as e:
        return False
    except Exception:
        return False


def get_extension(file_path: Union[str, Path]) -> str:
    """
    Description: 파일 유형을 가져오는 함수

    Args:
        file_path (str): 파일 경로

    Returns:
        str: 파일 유형
    """
    return os.path.splitext(file_path)[1]


# 파일 확장자에 따라 적절한 함수를 호출하여 파일을 읽어오는 함수
def read_file_by_extension(
    file_path: Union[str, Path], read_line_by_line: bool = False
) -> Union[List[str], str, dict]:
    """
    Description: 파일 확장자에 따라 파일 읽기를 지원하는 함수

    Args:
        file_path (str): 파일 경로
        read_line_by_line (bool, optional): txt, log, py 파일 형태의 데이터에서 한줄씩 읽어 List로 받아야 할 경우 추가 . Defaults to False.

    Raises:
        Exception: 현재 지원하지 않는 유형의 데이터일 경우
                    지원하는 데이터 유형 : txt, log, json, py, csv

    Returns:
        Union[List[str], str, dict]:
    """
    extension = get_extension(file_path=file_path)
    match extension:
        case ExtensionType.TXT:
            return read_file(file_path=file_path, read_line_by_line=read_line_by_line)
        case ExtensionType.CSV:
            return read_csv(file_path=file_path)
        case ExtensionType.JSON:
            return read_json(file_path=file_path)
        case ExtensionType.LOG:
            return read_file(file_path=file_path, read_line_by_line=read_line_by_line)
        case ExtensionType.PY:
            return read_file(file_path=file_path, read_line_by_line=read_line_by_line)
        case _:
            raise Exception


# 파일 확장자에 따라 적절한 함수를 호출하여 파일에 내용을 쓰는 함수
def write_file_by_extension(
    file_path: Union[str, Path], data: Any, mode: str = "w"
) -> bool:
    """
    Description: 파일 확장자와 mode에 따라 파일 쓰기를 지원하는 함수

    Args:
        file_path (str): 파일 경로
        mode (str, optional):  파일 쓰기 모드(지원하는 모드는 "a", "w"). Defaults to w.

    Raises:
        Exception: 현재 지원하지 않는 유형의 데이터일 경우
                    지원하는 데이터 유형 : txt, log, json, py, csv

    Returns:
        bool: 쓰기 성공하면 True, 실패하면 False
    """
    extension = get_extension(file_path=file_path)
    match extension:
        case ExtensionType.TXT:
            return write_file(file_path=file_path, data=data, mode=mode)
        case ExtensionType.CSV:
            return write_csv(file_path=file_path, data=data, mode=mode)
        case ExtensionType.JSON:
            return write_json(file_path=file_path, data=data, mode=mode)
        case ExtensionType.LOG:
            return write_file(file_path=file_path, data=data, mode=mode)
        case ExtensionType.PY:
            return write_file(file_path=file_path, data=data, mode=mode)
        case _:
            raise Exception


# hash 변환할 목록 정리
class HashChangeKind(Enum):
    GENERAL = "general"
    EXAMPLE = "example"


def text_to_hash(text: str, kind: HashChangeKind = HashChangeKind.GENERAL) -> str:
    """
    Description: 이 함수는 입력된 문자열을 MD5 해시로 변환하여 반환합니다.

    Args:
        text (str): 해시로 변환할 문자열입니다.
        kind (HashChangeKind, optional): 해시 변환 종류입니다. Defaults to HashChangeKind.GENERAL.

    Returns:
        str: 변환된 해시 문자열입니다.
    """
    hash_ = hashlib.md5(text.encode())
    match kind:
        case HashChangeKind.GENERAL:
            return hash_.hexdigest()
        case HashChangeKind.EXAMPLE:
            return "ex" + hash_.hexdigest()
        case _:
            raise ValueError


def create_folder(path: str) -> bool:
    """
    Description : 이 함수는 새로운 폴더를 생성하는 함수입니다.

    Args:
        path (str): 새로운 파일을 생성할 경로.

    Returns:
        bool
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Folder '{path}' created successfully!")
            return True
        else:
            print(f"Folder '{path}' already exists.")
            return False
    except OSError as e:
        print(f"Error: Failed to create folder '{path}'.")
        raise e


@dataclass
class ReplaceInfo:
    old_str: str
    new_str: str


# TODO
# exception 처리는 사용하는 방식에 따라 변경 가능
# 현재는 동일한 파일이 있을 경우 error 처리
def copy_and_replace_file(
    original_file_path: str, copy_file_path: str, replace_list: List[ReplaceInfo] = None
) -> bool:
    """
    Description : 파일 복사 시 사용되는 함수로 만약 replace 할 문자열이 있다면 ReplaceInfo class 사용할 것

    Args:
        original_file_path (str) : 복사할 파일의 원래 경로
        copy_file_path (str) : 복사될 파일의 경로
        replace_list (list in ReplaceInfo)

    Returns:
        bool
    """
    try:
        shutil.copy(original_file_path, copy_file_path)

        if replace_list:
            # 파일 읽기
            with open(copy_file_path, "r", encoding="utf-8") as file:
                file_data = file.read()

            # 문자열 변경
            for replace in replace_list:
                file_data = file_data.replace(replace.old_str, replace.new_str)

            # 수정된 내용 저장
            with open(copy_file_path, "w", encoding="utf-8") as file:
                file.write(file_data)

        return True

    except shutil.SameFileError as sf:
        return False
