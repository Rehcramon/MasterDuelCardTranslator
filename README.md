# Master Duel Card Translator Project
A tool for translating card details in Yu-Gi-Oh! Master Duel. Short for MDCT. Use OCR to recognize text in cards.

## Quick Start
1. Download the latest release.
2. Unzip it.
3. Run `MDCT_PositionSetup.exe`. This is the last step to configure MDCT.
4. Run `MasterDuelCardTranslator.exe`. Please enjoy.

## Run with Code
0. Of course, install `Python 3` before start.
1. Install Tesseract executable. Add it to `PATH` (the environment variable).
2. Install `pyautogui` and `pytesseract` by `pip`.
3. Run `MDCT_UpdateSource.py` to create the database of names.
4. Copy the latest `cards.cdb` file from YGOPro. Rename it to `ygocore.cdb`.
5. Duplicate `_settings.json` and rename it to `settings.json`.
6. Run `MDCT_PositionSetup.py`. This is the last step to configure MDCT.
7. Run `MasterDuelCardTranslator.py`. Please enjoy.

## Update Databases
1. Run `MDCT_UpdateSource.exe` (or `.py`) to update the database of names.
2. Copy the latest `cards.cdb` file from YGOPro. Rename it to `ygocore.cdb`.
