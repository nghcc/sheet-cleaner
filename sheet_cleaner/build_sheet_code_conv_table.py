import json

from fontTools import ttLib


def get_conv_map():
    tt = ttLib.TTFont('D:/Downloads/簡譜字型(win7改版)/simpmusicbase.ttf')
    cmap = tt['cmap'].tables[0].cmap

    valid_codes = (129, 141, 143, 144, 157)
    conv_map = {code: get_target_code(cmap, tt.getGlyphName(code))
                for code in range(128, 159+1) if code not in valid_codes}
    return conv_map


def get_target_code(cmap, glyph_name):
    for _code, _glyph_name in cmap.items():
        if _glyph_name == glyph_name:
            return _code
    return None


with open('code_conv_map.json', 'wt') as f:
    json.dump(get_conv_map(), f, indent=2)
