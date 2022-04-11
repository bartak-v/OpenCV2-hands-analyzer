import os
import numpy as np
import cv2 as cv2
import matplotlib.pyplot as plt


class HandExtractor:
    def __init__(self, image_number="01"):
        self.image_number = image_number
        self.images = []
        self.spectrum = ["465", "525", "580", "625", "855"]

    def _create_and_change_into_folder(self, im_num):
        # Vytvoří a/nebo nastaví current work dir na složku
        # /results/im_num (zde jsou výsledky)
        dir = os.path.dirname(__file__)

        if(not os.path.isdir(os.path.join(dir, "results"))):
            os.mkdir("results")
        os.chdir(os.path.join(dir, "results"))

        if(not os.path.isdir(im_num)):
            os.mkdir(im_num)
        os.chdir(im_num)

    def set_image_number(self):
        # Nastavení čísla ruky, se kterou se bude pracovat dále
        capturing = True
        while(capturing):
            im_num = input("Vložte číslo obrázku (1-78):")
            if(not im_num.isdigit()):
                print("Zadejte celé číslo v rozmezí 1 - 78!")
                continue
            elif(int(im_num) > 78 or int(im_num) < 1):
                print("Zadejte celé číslo v rozmezí 1 - 78!")
            else:
                if(int(im_num) < 10 and not("0" in im_num)):
                    self.image_number = "0"+im_num
                else:
                    self.image_number = im_num
                capturing = False

    def load_images(self):
        # Načte obrázky x-té ruky ve všech spektrech
        dir = os.path.dirname(__file__)
        filepath = os.path.join(dir, 'hand_db', 'images')

        for spec in self.spectrum:
            string = os.path.join(filepath, "210"+self.image_number+"_"+spec+"nm.png")
            img = cv2.imread(string)
            self.images.append(img)

    def extract_hand(self):
        # Extrahuje z obrázků ruku a uloží jí jako ROI (Region of Interest)
        self._create_and_change_into_folder(self.image_number)
        for i in range(len(self.images)):
            image = self.images[i]
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)[1]

            # Nalezení kontur a setřídění podle plochy
            contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else contours[1]
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            # Nalezení "bounding box" a extrakce ROI (Region of Interest)
            for c in contours:
                x, y, w, h = cv2.boundingRect(c)
                ROI = image[y:y+h, x:x + w]
                break

            # Uložení ROI (dlaně s prsty) pro každou ruku ve všech spektrech
            mod = len(self.spectrum)
            filep='ROI_'+self.image_number+'_' + self.spectrum[i % mod]+'nm.png'
            cv2.imwrite(filep, ROI)
            print("Dlaň č. "+self.image_number+ "("+ self.spectrum[i % mod] +"nm) extrahována do results/"+self.image_number+"/" + filep)

    def process_all_hands(self):
        # Extrahuje ROI pro všechny ruce ve všech spektrech (dlouhý běh)
        # A vytvoří thinned verze všech fotek.
        for i in range(1, 78):
            if(i < 10):
                self.image_number = "0"+str(i)
            else:
                self.image_number = str(i)
            self.load_images()
            self.extract_hand()
            self.hand_thinning()

    def _naive_thinning(self, file, nm, show=False):
        # Naivní thinning, který nevede ke kvalitním výsledkům
        img = cv2.imread(file, 0)
        img = (255 - img)

        if(nm == "465"):
            minVal = 40
            maxVal = 60
        elif(nm == "525"):
            minVal = 40
            maxVal = 60
        elif(nm == "580"):
            minVal = 30
            maxVal = 70
        else:
            minVal = 20
            maxVal = 30
        img = cv2.Canny(img, minVal, maxVal)
        if(show):
            cv2.imshow("thin", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        img = cv2.ximgproc.thinning(img)
        img = (255 - img)

        file = 'THIN_'+self.image_number+'_' + nm + 'nm.png'
        cv2.imwrite(file, img)
        print("Dlaň č. "+self.image_number+ "("+ nm +"nm) ztenčena do results/"+self.image_number+"/" + file)


    def hand_thinning(self, show=False):
        # Thinning všech fotek jedné ruky
        for i in range(len(self.spectrum)):
            nm = self.spectrum[i]
            file = 'ROI_'+self.image_number+'_' + nm + 'nm.png'
            self._naive_thinning(file, nm, show)
