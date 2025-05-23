import os
import argparse
from PIL import Image, ImageOps, ImageColor

def parse_color(color):
    if isinstance(color, tuple):
        return color
    elif isinstance(color, str):
        try:
            return ImageColor.getrgb(color)
        except ValueError:
            raise ValueError(f"Неверный формат цвета: {color}")
    else:
        raise ValueError(f"Неверный тип цвета: {type(color)}")

def parse_thickness(thickness, image_size):
    if isinstance(thickness, str) and thickness.endswith('%'):
        percent = float(thickness.strip('%')) / 100
        return int(min(image_size) * percent)
    else:
        return int(thickness)

def parse_aspect_ratio(ratio):
    presets = {
        "square": (1, 1),
        "portrait": (4, 5),
        "story": (9, 16),
        "landscape": (16, 9)
    }
    if isinstance(ratio, tuple):
        return ratio
    elif isinstance(ratio, str):
        if ratio in presets:
            return presets[ratio]
        elif ':' in ratio:
            w, h = map(int, ratio.split(':'))
            return (w, h)
        else:
            raise ValueError(f"Неверный формат соотношения: {ratio}")
    else:
        raise ValueError(f"Неверный тип соотношения: {type(ratio)}")

def add_frame_to_image(
    input_path,
    output_path,
    aspect_ratio=(1, 1),
    border_thickness=50,
    border_color=(255, 255, 255),
    quality=95
):
    img = Image.open(input_path)
    original_width, original_height = img.size
    original_ratio = original_width / original_height

    aspect_ratio = parse_aspect_ratio(aspect_ratio)
    border_color = parse_color(border_color)
    border_thickness = parse_thickness(border_thickness, img.size)

    target_ratio = aspect_ratio[0] / aspect_ratio[1]

    # Вычисляем размеры
    if original_ratio > target_ratio:
        new_width = original_width
        new_height = int(original_width / target_ratio)
    else:
        new_height = original_height
        new_width = int(original_height * target_ratio)

    background = Image.new('RGB', (new_width + 2 * border_thickness, new_height + 2 * border_thickness), border_color)

    offset_x = (background.width - original_width) // 2
    offset_y = (background.height - original_height) // 2
    background.paste(img, (offset_x, offset_y))

    ext = os.path.splitext(output_path)[1].lower()
    save_kwargs = {}
    if ext in ['.jpg', '.jpeg']:
        save_kwargs['quality'] = quality
        save_kwargs['optimize'] = True
        save_kwargs['subsampling'] = 0

    background.save(output_path, **save_kwargs)
    print(f"Saved framed image: {output_path}")

def process_folder(
    input_folder='input',
    output_folder='output',
    aspect_ratio=(1, 1),
    border_thickness=50,
    border_color=(255, 255, 255),
    quality=95,
    frame_mode="frame"
):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            input_path = os.path.join(input_folder, filename)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_{frame_mode}{ext}"
            output_path = os.path.join(output_folder, output_filename)

            add_frame_to_image(
                input_path,
                output_path,
                aspect_ratio=aspect_ratio,
                border_thickness=border_thickness,
                border_color=border_color,
                quality=quality
            )

def main():
    parser = argparse.ArgumentParser(description="Добавить рамки к изображениям для Instagram и других соцсетей")
    parser.add_argument('--input', type=str, default='input', help='Папка с исходными изображениями')
    parser.add_argument('--output', type=str, default='output', help='Папка для сохранения изображений')
    parser.add_argument('--aspect', type=str, default='1:1', help='Соотношение сторон (например, 4:5, 1:1, "portrait")')
    parser.add_argument('--thickness', type=str, default='5%', help='Толщина рамки (в пикселях или в процентах, например "5%%" или "60")')
    parser.add_argument('--color', type=str, default='white', help='Цвет рамки (имя, hex-код или rgb)')
    parser.add_argument('--quality', type=int, default=95, help='Качество сохранения JPEG (1-100)')
    parser.add_argument('--framemode', type=str, default='frame', help='Метка добавляемая к имени файла')

    args = parser.parse_args()

    process_folder(
        input_folder=args.input,
        output_folder=args.output,
        aspect_ratio=args.aspect,
        border_thickness=args.thickness,
        border_color=args.color,
        quality=args.quality,
        frame_mode=args.framemode
    )

if __name__ == "__main__":
    main()
