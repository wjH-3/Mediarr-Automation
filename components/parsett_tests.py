from PTT import Parser, add_defaults
import regex
from PTT.transformers import (boolean)
from RTN import title_match

# Initialize parser and add default handlers
parser = Parser()
add_defaults(parser)
parser.add_handler("trash", regex.compile(r"\b(\w+rip|hc|((h[dq]|clean)(.+)?)?cam.?(rip|rp)?|(h[dq])?(ts|tc)(?:\d{3,4})?|tele(sync|cine)?|\d+[0o]+([mg]b)|\d{3,4}tc)\b"), boolean, {"remove": False})

# List of files to filter
files = [
    "The.Substance.2024.2160p.AMZN.WEB-DL.DDP5.1.H.265-Kitsune[TGx]", 
    "Substancja - The Substance 2024 [10Bit SDR UPSCALING] [2160p.WEB-DL.H265.E-AC3.5.1-AS76-FT] [ENG-Napisy PL] [Translator Google] [Alusia]", 
    "Субстанция / The Substance [2024 WEB-DL 1080p] MVO + Sub Rus Eng + Original Eng", 
    "Woman of the Hour 2023 1080p NF WEB-DL DDP5 1 Atmos H 264-FLUX",
    "【高清影视之家发布 www.WHATMV.com】致命约会[简繁英字幕].Woman.of.the.Hour.2024.1080p.NF.WEB-DL.x264.DDP5.1.Atmos-SONYHD",
    "A.Garota.da.Vez.2024.1080p.WEB-DL.EAC3.AAC.DUAL.5.1",
    "[superseed.byethost7.com] Woman.of.the.Hour.2023.PL.WEB-DL.XviD-K83.avi.ts",
    "The.Substance.2024.V.4.2024.HDTS.c1nem4.x264-SUNSCREEN[TGx]",
    "From S01 2160p WEB-DL DDP5.1 H.265-TEPES",
    "Spiral: From the Book of Saw (2021) UHD BDRemux 2160p от селезень",
    "The Continental: From the World of John Wick [S01] (2023) WEB-DL-HEVC 2160p от NewComers",
    "From.S01E01.Long.Days.Journey.Into.Night.2160p.WEB-DL.DDP5.1.x265-TEPES[rartv]",
    "2012 2009 1080p Blu-ray Remux AVC DTS-HD MA 5.1 - KRaLiMaRKo",
    "Valiente 4K UHD 2009 2012 HDR TRIAL SPANISH BDRip x264",
    "2012 / 2012 (2009) UHD BDRemux 2160p от селезень | 4K | HDR | D A | Лицензия"
]

def main(imdb_title):
    # Array to store filtered files
    filtered_files = []

    # Filter out unwanted files
    for file in files:

        result = parser.parse(file)
        
        # Check for 'trash' and 'upscaled' fields and apply filters
        is_trash = result.get('trash', False)
        is_upscaled = result.get('upscaled', False)
        
        # Append the file if it's neither trash nor upscaled
        if not is_trash and not is_upscaled:
            title = result.get('title')

            # Perform title matching
            match = title_match(imdb_title, title)

            # If no title match, skip this file
            if not match:
                continue

            filtered_files.append((file, result.get('title', 'Unknown Title')))

    # Print out the filtered files in a numbered list
    if filtered_files:
        print("\nFiltered Files:")
        for idx, (file, title) in enumerate(filtered_files, start=1):
            print(f"{idx}. {file} (Title: {title})")
    else:
        print("\nNo matching files found.")

# Allow direct script execution for testing
if __name__ == "__main__":
    test_title = "2012"
    main(test_title)
