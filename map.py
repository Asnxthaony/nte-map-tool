import json
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

MAP_EDGE_SIZE = 687134
MAP_TILE_SIZE = 512
MAP_TILE_COUNT = 44
MAP_SIZE = MAP_TILE_SIZE * MAP_TILE_COUNT

MAP_SCALE = MAP_EDGE_SIZE / MAP_SIZE
MAP_CENTER_X = -40532.004
MAP_CENTER_Y = 131446.33


def parse_asset_path(asset_path: str) -> Optional[Path]:
    """
    将形如 /Game/UI/UI/minimap/bigworldmap/map_bigworld_10001.map_bigworld_10001 的路径转换为 bigworldmap/map_bigworld_10001.webp
    """

    marker = "/Game/UI/UI/minimap/"
    if marker not in asset_path:
        return None

    rel_path = asset_path.split(marker, 1)[1]
    rel_path = rel_path.split(".", 1)[0]

    return Path(rel_path).with_suffix(".webp")


def load_and_stitch(data, tile_size=512, output_path="output.webp"):
    with open(data, "r", encoding="utf-8") as f:
        data = json.load(f)

    tile_count_x = data["TileCountX"]
    tile_count_y = data["TileCountY"]
    tile_datas = data["TileImageDatas"]

    expected = tile_count_x * tile_count_y
    if len(tile_datas) != expected:
        print(f"WARN: 瓦片数量 ({len(tile_datas)}) 与预期 ({expected}) 不一致")

    total_width = tile_count_x * tile_size
    total_height = tile_count_y * tile_size
    bigmap_image = Image.new("RGBA", (total_width, total_height))

    for index, tile_data in enumerate(tile_datas):
        asset_path = tile_data["TileImage"]["AssetPathName"]
        img_path = parse_asset_path(asset_path)

        try:
            tile_img = Image.open(img_path).convert("RGBA")
        except FileNotFoundError:
            print(f"WARN: 找不到瓦片：{img_path}")
            tile_img = Image.new("RGBA", (tile_size, tile_size), (0, 0, 0, 0))

        col = index % tile_count_x
        row = index // tile_count_x

        x = col * tile_size
        y = row * tile_size

        bigmap_image.paste(tile_img, (x, y))
        print(f"已粘贴瓦片 [{row},{col}] <- {img_path}")

    bigmap_image.save(output_path)
    print(f"拼接完成，保存至 {output_path}")

    return bigmap_image


def world_pos_to_map_pos(world_x: float, world_y: float) -> Tuple[int, int]:
    map_x = (world_x - MAP_CENTER_X) / MAP_SCALE
    map_y = (world_y - MAP_CENTER_Y) / MAP_SCALE

    map_x = MAP_SIZE // 2 + map_x
    map_y = MAP_SIZE // 2 + map_y

    return int(map_x), int(map_y)


def draw_marker(
    image: Image.Image,
    x: int,
    y: int,
    text: str = "",
    color: str = "#fb3838",
    text_color: str = "#0099ff",
    radius: int = 20,
):
    draw = ImageDraw.Draw(image)

    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius), outline=color, width=2
    )
    if text:
        font = ImageFont.truetype("fonts/SimHei.ttf", 24)
        draw.text((x + radius + 2, y - radius), text, fill=text_color, font=font)


if __name__ == "__main__":
    bigmap = load_and_stitch(
        "XL_map_bigworld_test.json",
        tile_size=MAP_TILE_SIZE,
        output_path="bigmap_total.png",
    )

    # 载具兄弟-阶段1
    map_x, map_y = world_pos_to_map_pos(-101892.14, 93486.65)
    draw_marker(bigmap, x=map_x, y=map_y, text="载具兄弟-阶段1")

    # 载具兄弟-阶段2
    map_x, map_y = world_pos_to_map_pos(-101411.055, 75400.87)
    draw_marker(bigmap, x=map_x, y=map_y, text="载具兄弟-阶段2")

    # 载具兄弟-阶段3
    map_x, map_y = world_pos_to_map_pos(-127812.64, 68254.4)
    draw_marker(bigmap, x=map_x, y=map_y, text="载具兄弟-阶段3")

    # 载具兄弟-阶段4/5
    map_x, map_y = world_pos_to_map_pos(-98927.58, 69289.6)
    draw_marker(bigmap, x=map_x, y=map_y, text="载具兄弟-阶段4/5")

    bigmap.save("bigmap_with_marker.png")
