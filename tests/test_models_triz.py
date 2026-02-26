def test_triz_principle_model():
    from app.models.triz import TRIZPrinciple

    p = TRIZPrinciple(
        number=1,
        name_en="Segmentation",
        name_ko="분할",
        description="Divide an object into independent parts.",
    )
    assert p.number == 1
    assert p.name_ko == "분할"

def test_load_triz_principles():
    from app.models.triz import load_triz_principles

    principles = load_triz_principles()
    assert len(principles) == 40
    assert principles[0].number == 1
    assert principles[0].name_en == "Segmentation"
    assert principles[39].number == 40
    assert principles[39].name_en == "Composite Materials"
