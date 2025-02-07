import glob
import os
import cv2
import shutil

from db import CompetitionDatabase
from reader import scan_image

qr_detector = cv2.QRCodeDetector()
db = CompetitionDatabase()

IMAGE_INPUT_DIR = "../unprocessed_images"
IMAGE_OUTPUT_DIR = "../processed_images"

CROP_AMNT = 0.5


def read_images():
    files = glob.glob(f"{IMAGE_INPUT_DIR}/*.jpg")
    images = [(file, cv2.imread(file, cv2.IMREAD_GRAYSCALE)) for file in files]
    return images


def read_qr(image):
    data, _, _ = qr_detector.detectAndDecode(image)
    return data


def crop_times(image):
    height = int(image.shape[1] * CROP_AMNT)

    return image[height:, :]


def process_images():
    images = read_images()

    image_data = []

    for image_w_name in images:
        name, image = image_w_name
        data = read_qr(image)
        if data is not None:
            competitor_id, event, round = data.split("-")
        else:
            competitor_id = event = round = None

        image_data.append((image, name, competitor_id, event, round))

    for i in range(0, len(image_data), 5):
        img_group_info = image_data[i : i + 5]

        img_group = [crop_times(img[0]) for img in img_group_info]

        responses = scan_image(img_group)

        for img_info, response in zip(img_group_info, responses):
            image, name, comp_id, event, round = img_info

            times = [item[1] for item in sorted(response.items(), key=lambda x: x[0])]

            pk = db.add_result(
                competitor_id=comp_id, event=event, round_num=round, times=times
            )

            new_file_name = f"{pk}.jpg"
            new_file_path = os.path.join(IMAGE_OUTPUT_DIR, new_file_name)
            shutil.move(name, new_file_path)


if __name__ == "__main__":
    process_images()
