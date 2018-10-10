import os
import time
import re
import jinja2
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
import cv2

def load():
    result = []
    with open("result") as f:
        content = f.read()
        lines = content.split("\n")
        state = 0
        qa = None
        i = 1
        for line in lines:
            if not line:
                continue
            if re.match(r"===", line):
                qa = {"id": i}
                state = 1
            if state == 1 and re.match(r"Q:", line):
                qa["q"] = line[3:]
            if state == 1 and re.match(r"A:", line):
                qa["a"] = line[3:]
            if state == 1 and re.match(r"vote:", line):
                result.append(qa)
                i += 1
                state = 0
    return result

def to_html(items):
    loader = jinja2.FileSystemLoader(searchpath="./")
    env = jinja2.Environment(loader=loader)
    template = env.get_template("template.html")
    content = template.render(items=items)
    ts = int(time.time()*1000)
    filename = "htmls/{}.html".format(ts)
    with open(filename, "w") as f:
        f.write(content)

def crop_images():
    img_files = os.listdir("./images")
    for img_file in img_files:
        out_name = "new_" + img_file
        img_path = os.path.join("./images", img_file)
        out_path = os.path.join("./images", out_name)
        print(img_path, out_path)
        img = cv2.imread(img_path)
        crop_img = img[:2000, :550]
        cv2.imwrite(out_path, crop_img)

if __name__ == "__main__":
    #all_items = load()
    ##to_html(all_items)
    #for i in range(0, len(all_items), 8):
    #    start = i
    #    end = min(i+8, len(all_items))
    #    items = all_items[start:end]
    #    to_html(items)
    crop_images()
