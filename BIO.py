from HandExtractor import HandExtractor

he = HandExtractor()
he.set_image_number()
he.load_images()
he.extract_hand()
he.hand_thinning()

#Alternativně lze místo řádků 4-7 volat:
#he.process_all_hands() # dlouhý běh, zpracuje všechny fotky