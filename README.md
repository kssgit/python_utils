# python_utils

개발하면서 자주 사용하는 util 함수 정리

아직 주니어 개발자이기 때문에 효율적이지 못한 부분이 있을 수 있습니다.
문제가 있을 경우 issue에 글을 남겨주세요! 🙏🙏🙏🙏🙏🙏

# Python version

python 3.10 이상

# common_func

## 함수 리스트 

### common_request 
request method 유형에 따라 request를 보내는 함수

### convert_data_size
데이터 크기 단위 변환 함수

### read_*
확장자별 파일 읽기 함수

### write_*
확장자별 파일 쓰기 함수

### text_to_hash
enum class인 HashChangeKind에 정의된 목록 종류별 hash 변환

### create_folder
입력한 path에 새로운 directory를 생성하는 함수


### copy_and_replace_file

파일을 복사하는 함수. 변환할 문자열이 있다면 list에 ReplaceInfo class를 담아 요청