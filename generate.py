accounts = [
    ('67193564@N03', 'National Library of Australia Commons'),
    ('32605636@N06', 'State Library of Queensland'),
    ('107895189@N03', 'Tasmanian Archive and Heritage Office Commons'),
    ('27331537@N06', 'State Records NSW'),
    ('24785917@N03', 'Powerhouse Museum'),
    ('33147718@N05', 'Australian National Maritime Museum Commons'),
    ('29454428@N08', 'State Library of NSW'),
    ('30115723@N02', 'Australian War Memorial'),
]


template = '__import__("flickr_search").client("{}", "{}")'


for uid, username in accounts:
    filename = username.lower().replace(' ', '_') + '_gen.py'
    print(filename)
    with open(filename, 'w') as fh:
        fh.write(template.format(uid, username))
