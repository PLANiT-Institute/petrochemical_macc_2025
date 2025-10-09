#!/usr/bin/env python3
"""
Translate Korean Data to English in Excel File
Systematically identify and translate all Korean text to English
"""

import pandas as pd
import numpy as np
from pathlib import Path
import openpyxl
from openpyxl import load_workbook
import re

class KoreanToEnglishTranslator:
    def __init__(self):
        """Initialize with Excel file paths"""
        self.input_path = "../data/Korean_Petrochemical_MACC_Model_Updated_Detailed.xlsx"
        self.output_path = "../data/Korean_Petrochemical_MACC_Model_English.xlsx"

        # Korean to English translation mappings
        self.translation_dict = {
            # Company names (major Korean petrochemical companies)
            'SK케미칼': 'SK Chemical',
            'SK이노베이션': 'SK Innovation',
            'LG화학': 'LG Chem',
            '롯데케미칼': 'Lotte Chemical',
            '한화케미칼': 'Hanwha Chemical',
            '삼성석유화학': 'Samsung Petrochemical',
            'S-Oil': 'S-Oil',
            'GS칼텍스': 'GS Caltex',
            '현대오일뱅크': 'Hyundai Oilbank',
            'SK종합화학': 'SK Total Petrochemicals',
            'LG석유화학': 'LG Petrochemicals',
            '대림산업': 'Daelim Industrial',
            '금호석유화학': 'Kumho Petrochemical',
            '호남석유화학': 'Honam Petrochemical',
            '여수산업단지': 'Yeosu Industrial Complex',

            # Additional Korean companies
            'SK지오센트릭': 'SK Geocentric',
            'SK어드밴스드': 'SK Advanced',
            'SK에너지': 'SK Energy',
            'SK인천석유화학': 'SK Incheon Petrochemical',
            '롯데GS화학': 'Lotte GS Chemical',
            '롯데베르살리스엘라스토머스': 'Lotte Versalis Elastomers',
            '롯데이네오스화학': 'Lotte INEOS Chemical',
            '롯데엠시시': 'Lotte MCC',
            '한화솔루션': 'Hanwha Solutions',
            '한화토탈에너지스': 'Hanwha TotalEnergies',
            '한화임팩트': 'Hanwha Impact',
            'HD현대케미칼': 'HD Hyundai Chemical',
            'HD현대OCI': 'HD Hyundai OCI',
            'HDC현대EP': 'HDC Hyundai EP',
            'DL케미칼': 'DL Chemical',
            '금호폴리켐': 'Kumho Polychem',
            '금호미쓰이화학': 'Kumho Mitsui Chemical',
            '금호피앤비화학': 'Kumho P&B Chemical',
            '여천NCC': 'Yeochon NCC',
            '대한유화': 'Daehan Oil Chemical',
            '태광산업': 'Taekwang Industrial',
            '효성화학': 'Hyosung Chemical',
            '삼양화성': 'Samyang Chemical',
            '삼양이노켐': 'Samyang Innochem',
            '삼남석유화학': 'Samnam Petrochemical',
            '폴리미래': 'Poly Mirae',
            '울산피피': 'Ulsan PP',
            '울산아로마틱스': 'Ulsan Aromatics',
            '한국이네오스스티롤루션': 'Korea INEOS Styrolution',
            'SH에너지화학': 'SH Energy Chemical',
            '한국바스프': 'BASF Korea',
            '동서석유화학': 'Dongseo Petrochemical',
            '한국트린지오': 'Korea Trinseo',
            '한솔케미칼': 'Hansol Chemical',
            '한국알콜산업': 'Korea Alcohol Industrial',
            '이수화학': 'ISU Chemical',
            '애경케미칼': 'Aekyung Chemical',
            '용산케미칼': 'Yongsan Chemical',
            '코리아피티지': 'Korea PTG',
            '구다우케미칼': 'Downing Chemical',
            'Bluecube케미칼': 'Bluecube Chemical',
            '코오롱인더스트리': 'Kolon Industries',
            '국도화학': 'Kukdo Chemical',
            '피유코어': 'PU Core',
            'KPX케미칼': 'KPX Chemical',
            '아케마': 'Arkema',
            '비틀라카본코리아': 'Birla Carbon Korea',
            '오리온엔지니어드카본즈': 'Orion Engineered Carbons',

            # Locations (Korean petrochemical industrial complexes)
            '여수': 'Yeosu',
            '울산': 'Ulsan',
            '대산': 'Daesan',
            '서산': 'Seosan',
            '온산': 'Onsan',
            '창원': 'Changwon',
            '부산': 'Busan',
            '인천': 'Incheon',
            '김천': 'Gimcheon',
            '구미': 'Gumi',
            '포항': 'Pohang',
            '광양': 'Gwangyang',
            '당진': 'Dangjin',
            '평택': 'Pyeongtaek',
            '아산': 'Asan',
            '천안': 'Cheonan',
            '제천': 'Jecheon',
            '충주': 'Chungju',
            '청주': 'Cheongju',
            '진주': 'Jinju',
            '마산': 'Masan',
            '통영': 'Tongyeong',
            '거제': 'Geoje',
            '고성': 'Goseong',
            '남해': 'Namhae',
            '하동': 'Hadong',
            '사천': 'Sacheon',
            '밀양': 'Miryang',
            '양산': 'Yangsan',
            '김해': 'Gimhae',
            '전주': 'Jeonju',
            '군산': 'Gunsan',
            '나주': 'Naju',
            '익산': 'Iksan',
            '시흥': 'Siheung',

            # Process types
            '나프타분해': 'Naphtha Cracker',
            '방향족': 'Aromatics',
            'BTX': 'BTX Plant',
            '올레핀': 'Olefins',
            '유틸리티': 'Utility',
            '스팀': 'Steam',
            '전력': 'Power',
            '냉각': 'Cooling',
            '가열': 'Heating',

            # Products
            '에틸렌': 'Ethylene',
            '프로필렌': 'Propylene',
            '부타디엔': 'Butadiene',
            '벤젠': 'Benzene',
            '톨루엔': 'Toluene',
            '자일렌': 'Xylene',
            '스티렌': 'Styrene',

            # Additional chemical products
            '초산': 'Acetic Acid',
            '초산비닐': 'Vinyl Acetate',
            '에탄올': 'Ethanol',
            '초산에틸': 'Ethyl Acetate',
            '알킬벤젠': 'Alkylbenzene',
            '카본블랙': 'Carbon Black',
            '페놀': 'Phenol',
            '아세톤': 'Acetone',
            '옥탄올': 'Octanol',
            '부탄올': 'Butanol',
            '석유수지': 'Petroleum Resin',
            '카프로': 'Caprolactam',

            # Fuel types
            '천연가스': 'Natural Gas',
            'LNG': 'LNG',
            '나프타': 'Naphtha',
            '중유': 'Heavy Oil',
            '경유': 'Diesel',
            '휘발유': 'Gasoline',
            '전력': 'Electricity',
            '스팀': 'Steam',

            # Units and technical terms
            '톤': 'ton',
            '천톤': 'kton',
            '만톤': '10kton',
            '년': 'year',
            '개월': 'month',
            '일': 'day',
            '시간': 'hour',
            '분': 'minute',
            '초': 'second',
            '설비': 'Facility',
            '공장': 'Plant',
            '단지': 'Complex',
            '산업단지': 'Industrial Complex',
            '석유화학단지': 'Petrochemical Complex',
            '제조': 'Manufacturing',
            '생산': 'Production',
            '가동': 'Operation',
            '운전': 'Operation',
            '정지': 'Shutdown',
            '보수': 'Maintenance',
            '점검': 'Inspection',

            # Technology and equipment terms
            '분해로': 'Cracker Furnace',
            '증류탑': 'Distillation Column',
            '반응기': 'Reactor',
            '열교환기': 'Heat Exchanger',
            '압축기': 'Compressor',
            '터빈': 'Turbine',
            '보일러': 'Boiler',
            '냉각탑': 'Cooling Tower',
            '저장탱크': 'Storage Tank',
            '배관': 'Piping',
            '펌프': 'Pump',
            '밸브': 'Valve',

            # Common Korean words that might appear
            '회사': 'Company',
            '기업': 'Corporation',
            '주식회사': 'Co., Ltd.',
            '(주)': 'Co., Ltd.',
            '그룹': 'Group',
            '계열사': 'Affiliate',
            '자회사': 'Subsidiary',
            '본사': 'Headquarters',
            '지사': 'Branch',
            '사업부': 'Business Unit',
            '부문': 'Division',
            '팀': 'Team',
            '과': 'Department',
            '센터': 'Center',
            '연구소': 'Research Institute',
            '기술원': 'Technology Institute'
        }

    def has_korean(self, text):
        """Check if text contains Korean characters"""
        if pd.isna(text) or not isinstance(text, str):
            return False
        korean_pattern = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
        return bool(korean_pattern.search(text))

    def translate_text(self, text):
        """Translate Korean text to English"""
        if pd.isna(text) or not isinstance(text, str):
            return text

        # If no Korean characters, return as is
        if not self.has_korean(text):
            return text

        translated = text

        # Apply translations in order of length (longest first to avoid partial matches)
        sorted_translations = sorted(self.translation_dict.items(), key=lambda x: len(x[0]), reverse=True)

        for korean, english in sorted_translations:
            translated = translated.replace(korean, english)

        # If still has Korean after translation, mark it for manual review
        if self.has_korean(translated):
            print(f"⚠️  Manual review needed: '{text}' → '{translated}'")

        return translated

    def scan_excel_for_korean(self):
        """Scan Excel file and identify all Korean text"""
        print("🔍 Scanning Excel file for Korean text...")

        korean_found = {}

        # Load all sheets
        excel_file = pd.ExcelFile(self.input_path)

        for sheet_name in excel_file.sheet_names:
            print(f"   Scanning sheet: {sheet_name}")
            df = pd.read_excel(self.input_path, sheet_name=sheet_name)

            sheet_korean = []

            # Check all cells for Korean text
            for col in df.columns:
                # Check column headers
                if self.has_korean(str(col)):
                    sheet_korean.append(f"Column header: {col}")

                # Check cell values
                for idx, value in df[col].items():
                    if self.has_korean(str(value)):
                        sheet_korean.append(f"Row {idx}, Col '{col}': {value}")

            if sheet_korean:
                korean_found[sheet_name] = sheet_korean
                print(f"     Found {len(sheet_korean)} Korean entries")

        return korean_found

    def translate_excel_file(self):
        """Translate entire Excel file"""
        print("🔄 Translating Excel file from Korean to English...")

        # Copy file first
        import shutil
        shutil.copy2(self.input_path, self.output_path)

        # Load workbook
        book = load_workbook(self.output_path)

        with pd.ExcelWriter(self.output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            excel_file = pd.ExcelFile(self.input_path)

            for sheet_name in excel_file.sheet_names:
                print(f"   Translating sheet: {sheet_name}")
                df = pd.read_excel(self.input_path, sheet_name=sheet_name)

                # Translate column headers
                new_columns = {}
                for col in df.columns:
                    translated_col = self.translate_text(str(col))
                    if translated_col != str(col):
                        new_columns[col] = translated_col
                        print(f"     Column: '{col}' → '{translated_col}'")

                if new_columns:
                    df = df.rename(columns=new_columns)

                # Translate cell values
                translated_count = 0
                for col in df.columns:
                    for idx in df.index:
                        original_value = df.at[idx, col]
                        if self.has_korean(str(original_value)):
                            translated_value = self.translate_text(str(original_value))
                            if translated_value != str(original_value):
                                df.at[idx, col] = translated_value
                                translated_count += 1
                                print(f"     Row {idx}, '{col}': '{original_value}' → '{translated_value}'")

                print(f"     Translated {translated_count} cells in {sheet_name}")

                # Write translated sheet
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✅ Translation complete: {self.output_path}")

    def create_translation_report(self, korean_found):
        """Create a report of translations needed"""
        print("📊 Creating translation report...")

        report_data = []
        for sheet_name, korean_entries in korean_found.items():
            for entry in korean_entries:
                parts = entry.split(': ', 1)
                location = parts[0]
                korean_text = parts[1] if len(parts) > 1 else ""
                translated_text = self.translate_text(korean_text)

                report_data.append({
                    'sheet': sheet_name,
                    'location': location,
                    'korean_original': korean_text,
                    'english_translation': translated_text,
                    'needs_manual_review': self.has_korean(translated_text)
                })

        report_df = pd.DataFrame(report_data)
        report_path = Path("../outputs/korean_translation_report.csv")
        report_df.to_csv(report_path, index=False)
        print(f"   Report saved: {report_path}")

        # Summary
        total_entries = len(report_data)
        manual_review = report_df['needs_manual_review'].sum()
        auto_translated = total_entries - manual_review

        print(f"   Total Korean entries: {total_entries}")
        print(f"   Auto-translated: {auto_translated}")
        print(f"   Need manual review: {manual_review}")

        return report_df

    def run_translation(self):
        """Run complete translation process"""
        print("🚀 KOREAN TO ENGLISH TRANSLATION")
        print("=" * 80)
        print(f"📁 Input: {self.input_path}")
        print(f"📁 Output: {self.output_path}")
        print()

        try:
            # Scan for Korean text
            korean_found = self.scan_excel_for_korean()

            if not korean_found:
                print("✅ No Korean text found in the file!")
                return

            # Create translation report
            report_df = self.create_translation_report(korean_found)

            # Perform translation
            self.translate_excel_file()

            print("\n🎯 TRANSLATION SUMMARY:")
            for sheet, entries in korean_found.items():
                print(f"   {sheet}: {len(entries)} translations")

            print(f"\n📁 Translated file: {self.output_path}")
            print(f"📊 Translation report: ../outputs/korean_translation_report.csv")

            return self.output_path

        except Exception as e:
            print(f"❌ Translation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    translator = KoreanToEnglishTranslator()
    output_file = translator.run_translation()

    print("\n✅ KOREAN TO ENGLISH TRANSLATION COMPLETE!")
    print("📁 Use the English version for all future analysis")