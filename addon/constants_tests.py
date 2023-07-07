"""For testing only. Do NOT import or use variables in this file!"""
from constants import *


# For testing only
NORMAL_CARD_TEMPLATE_QFMT = """\
<table>
    <tr>
        <td>
            <h1 class="term">{{term}}</h1>
            <span>{{pronunciation}}</span>
            <div class="pronounce">
                <span class="phonetic">UK[{{uk}}]</span>
                <span class="phonetic">US[{{us}}]</span>
            </div>
            <div class="definition">Tap To View</div>
            <div class="definition_en"></div>
        </td>
        <td style="width: 33%;">
            {{image}}
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{{phrase0}}</td><td>{{pplaceHolder0}}</td></tr>
    <tr><td class="phrase">{{phrase1}}</td><td>{{pplaceHolder1}}</td></tr>
    <tr><td class="phrase">{{phrase2}}</td><td>{{pplaceHolder2}}</td></tr>
</table>
<table>
    <tr><td class="sentence">{{sentence0}}</td><td>{{splaceHolder0}}</td></tr>
    <tr><td class="sentence">{{sentence1}}</td><td>{{splaceHolder1}}</td></tr>
    <tr><td class="sentence">{{sentence2}}</td><td>{{splaceHolder2}}</td></tr>
</table>
"""
NORMAL_CARD_TEMPLATE_AFMT = """\
<table>
    <tr>
        <td>
        <h1 class="term">{{term}}</h1>
            <span>{{pronunciation}}</span>
            <div class="pronounce">
                <span class="phonetic">UK[{{uk}}]</span>
                <span class="phonetic">US[{{us}}]</span>
            </div>
            <div class="definition">{{definition}}</div>
            <div class="definition_en">{{definition_en}}</div>
            <div class="exam_type">{{exam_type}}</div>
        </td>
        <td style="width: 33%;">
            {{image}}
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{{phrase0}}</td><td>{{phrase_explain0}}</td></tr>
    <tr><td class="phrase">{{phrase1}}</td><td>{{phrase_explain1}}</td></tr>
    <tr><td class="phrase">{{phrase2}}</td><td>{{phrase_explain2}}</td></tr>
</table>
<table>
    <tr><td class="sentence">{{sentence0}}</td><td>{{sentence_explain0}}</td></tr>
    <tr><td class="sentence">{{sentence1}}</td><td>{{sentence_explain1}}</td></tr>
    <tr><td class="sentence">{{sentence2}}</td><td>{{sentence_explain2}}</td></tr>
</table>
"""

BACKWARDS_CARD_TEMPLATE_QFMT = """\
<table>
    <tr>
        <td>
        <h1 class="term"></h1>
            <div class="pronounce">
                <span class="phonetic">UK[Tap To View]</span>
                <span class="phonetic">US[Tap To View]</span>
            </div>
            <div class="definition">{{definition}}</div>
            <div class="definition_en">{{definition_en}}</div>
        </td>
        <td style="width: 33%;">
            {{image}}
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{{pplaceHolder0}}</td><td>{{phrase_explain0}}</td></tr>
    <tr><td class="phrase">{{pplaceHolder1}}</td><td>{{phrase_explain1}}</td></tr>
    <tr><td class="phrase">{{pplaceHolder2}}</td><td>{{phrase_explain2}}</td></tr>
</table>
<table>
    <tr><td class="sentence">{{splaceHolder0}}</td><td>{{sentence_explain0}}</td></tr>
    <tr><td class="sentence">{{splaceHolder1}}</td><td>{{sentence_explain1}}</td></tr>
    <tr><td class="sentence">{{splaceHolder2}}</td><td>{{sentence_explain2}}</td></tr>
</table>
"""
BACKWARDS_CARD_TEMPLATE_AFMT = NORMAL_CARD_TEMPLATE_AFMT


if __name__ == '__main__':
    fieldGroup = FieldGroup()
    normal_qfmt = normal_card_template_qfmt(fieldGroup)
    assert normal_qfmt == NORMAL_CARD_TEMPLATE_QFMT
    normal_afmt = normal_card_template_afmt(fieldGroup)
    assert normal_afmt == NORMAL_CARD_TEMPLATE_AFMT

    backwards_qftm = backwards_card_template_qfmt(fieldGroup)
    assert backwards_qftm == BACKWARDS_CARD_TEMPLATE_QFMT
    backwards_afmt = backwards_card_template_afmt(fieldGroup)
    assert backwards_afmt == BACKWARDS_CARD_TEMPLATE_AFMT
    print("OK!")
