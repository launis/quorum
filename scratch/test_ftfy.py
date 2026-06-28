import ftfy

def test():
    # Simulate a mojibake string.
    mojibake = b'Kustannus- ja Toimitusketjuh\xc3\xa4iri\xc3\xb6t'.decode('latin-1')
    print("Mojibake:", repr(mojibake))
    print("Fixed mojibake:", repr(ftfy.fix_text(mojibake)))
    
    clean = 'Kustannus- ja Toimitusketjuhäiriöt'
    print("Clean:", repr(clean))
    print("Fixed clean:", repr(ftfy.fix_text(clean)))

test()
