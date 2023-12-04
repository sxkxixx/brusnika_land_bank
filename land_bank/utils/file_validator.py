from fastapi import UploadFile


class FileValidator:
    SIGNATURES = {
        'JPG': ['FF D8 FF DB', ],
        'JPEG': ['FF D8 FF E0', 'FF D8 FF E1'],
        'PNG': ['89 50 4E 47 0D 0A 1A 0A']
    }

    def __init__(self):
        pass

    async def is_valid_file(self, file: UploadFile) -> bool:
        result: bool = False
        try:
            data = await file.read(32)
            file_extends = self.__get_file_extends(file.content_type)
            for signature in self.SIGNATURES.get(file_extends):
                if signature in data:
                    result = True
                    break
        finally:
            await file.seek(0)
            return result

    def __get_file_extends(self, content_type: str) -> str:
        file_extends = content_type[content_type.find('/') + 1:]
        return file_extends.upper()
