def format_docs(docs):
        """
        Formatting retrieval output

        Args:
            docs (List[Document]): retrieval outputs

        Returns:
            str: concat retrieved places
        """
        return "\n".join(doc.metadata["name"] for doc in docs)

def coll_name_mapping(text):
    ## 한글-영어 키보드 mapping
    kor_to_eng = {
        'ㄱ': 'r', 'ㄲ': 'R', 'ㄴ': 's', 'ㄷ': 'e', 'ㄸ': 'E',
        'ㄹ': 'f', 'ㅁ': 'a', 'ㅂ': 'q', 'ㅃ': 'Q', 'ㅅ': 't',
        'ㅆ': 'T', 'ㅇ': 'd', 'ㅈ': 'w', 'ㅉ': 'W', 'ㅊ': 'c',
        'ㅋ': 'z', 'ㅌ': 'x', 'ㅍ': 'v', 'ㅎ': 'g',
        'ㅏ': 'k', 'ㅐ': 'o', 'ㅑ': 'i', 'ㅒ': 'O', 'ㅓ': 'j',
        'ㅔ': 'p', 'ㅕ': 'u', 'ㅖ': 'P', 'ㅗ': 'h', 'ㅘ': 'hk',
        'ㅙ': 'ho', 'ㅚ': 'hl', 'ㅛ': 'y', 'ㅜ': 'n', 'ㅝ': 'nj',
        'ㅞ': 'np', 'ㅟ': 'nl', 'ㅠ': 'b', 'ㅡ': 'm', 'ㅢ': 'ml',
        'ㅣ': 'l'
    }
    
    result = ''
    for char in text:
        if '가' <= char <= '힣':
            char_code = ord(char) - ord('가')
            cho = char_code // 588 ## 초성
            jung = (char_code - (588 * cho)) // 28 ## 중성
            jong = char_code % 28 ## 종성성
            
            result += kor_to_eng[chr(ord('ㄱ') + cho)]
            result += kor_to_eng[chr(ord('ㅏ') + jung)]
            if jong > 0:
                result += kor_to_eng[chr(ord('ㄱ') + jong - 1)]
        else:
            result += char
    
    return result