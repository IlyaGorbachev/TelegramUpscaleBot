import cv2
from super_image import MdsrModel, ImageLoader
from PIL import Image



def func_upscale(path):
    image = cv2.imread(path)
#scale_percent = 60 percent of original size
    if image.shape[1] <= 500:
        scale_percent = 100
    elif image.shape[1] > 500 and image.shape[1] < 1000:
        scale_percent = 50
    elif image.shape[1] >= 1000:
        scale_percent= 30
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    image_resize = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, image_resize)
    image = Image.open(path)
    
    model = MdsrModel.from_pretrained('models', scale=3)
    inputs = ImageLoader.load_image(image)
    preds = model(inputs)

    ImageLoader.save_image(preds, 'aiupscale/output/scaled_3x.png')

    image = cv2.imread('aiupscale/output/scaled_3x.png')
    dst = cv2.fastNlMeansDenoisingColored(image, None, 6, 9, 4, 21)
    #Синтаксис: cv2.fastNlMeansDenoisingColored(P1, P2, float P3, float P4, int P5, int P6)

    #Параметры:
    #P1 — Исходный массив изображений
    #P2 — Целевой массив изображений
    #P3 — размер в пикселях патча шаблона, который используется для вычисления весов.
    #P4 — размер окна в пикселях, который используется для вычисления средневзвешенного значения для данного пикселя.
    #P5 – Параметр, регулирующий силу фильтра яркостной составляющей.
    #P6 — то же, что и выше, но для компонентов цвета // Не используется в изображении в градациях серого.

    cv2.imwrite("aiupscale/output/scaled_3x_denoise.png", dst)
