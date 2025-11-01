from tech_radar import generate_rings_from_excel

def test_generate_rings_from_excel():
    assert generate_rings_from_excel(r"tests\input\tech_radar.xlsx") == \
    [{'name': 'Adopt', 'color': '#5BA300', 'rank': 0}, {'name': 'Trial', 'color': '#009EB0', 'rank': 1}, {'name': 'Assess', 'color': '#C7BA00', 'rank': 2}, {'name': 'Hold', 'color': '#E09B96', 'rank': 3}]