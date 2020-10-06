import io
import json
from datetime import date, datetime, timedelta, timezone

import cv2
import numpy as np
from discord import Embed, File, Game
from discord.ext import commands as c
from PIL import Image, ImageDraw, ImageFont

from module import db, item

with open('../assets/login_bonus.json', encoding='utf-8') as f:
    df = json.load(f)

class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.Cog.listener()
    async def on_command(self, ctx):
        def overlay(cv_background_image, cv_overlay_image, point,):
            """
            [summary]
                OpenCV形式の画像に指定画像を重ねる
            Parameters
            ----------
            cv_background_image : [OpenCV Image]
            cv_overlay_image : [OpenCV Image]
            point : [(x, y)]
            Returns : [OpenCV Image]
            """
            overlay_height, overlay_width = cv_overlay_image.shape[:2]

            # OpenCV形式の画像をPIL形式に変換(α値含む)
            # 背景画像
            cv_rgb_bg_image = cv2.cvtColor(cv_background_image, cv2.COLOR_BGR2RGB)
            pil_rgb_bg_image = Image.fromarray(cv_rgb_bg_image)
            pil_rgba_bg_image = pil_rgb_bg_image.convert('RGBA')
            # オーバーレイ画像
            cv_rgb_ol_image = cv2.cvtColor(cv_overlay_image, cv2.COLOR_BGRA2RGBA)
            pil_rgb_ol_image = Image.fromarray(cv_rgb_ol_image)
            pil_rgba_ol_image = pil_rgb_ol_image.convert('RGBA')

            # composite()は同サイズ画像同士が必須のため、合成用画像を用意
            pil_rgba_bg_temp = Image.new('RGBA', pil_rgba_bg_image.size,
                                            (255, 255, 255, 0))
            # 座標を指定し重ね合わせる
            pil_rgba_bg_temp.paste(pil_rgba_ol_image, point, pil_rgba_ol_image)
            result_image = Image.alpha_composite(pil_rgba_bg_image, pil_rgba_bg_temp)

            # OpenCV形式画像へ変換
            cv_bgr_result_image = cv2.cvtColor(
                np.asarray(result_image), cv2.COLOR_RGBA2BGRA)

            return cv_bgr_result_image
        login_timezone = timezone(timedelta(hours=+0), 'UTC')
        # timezone = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(login_timezone)
        login_data = db.player.login.get(ctx.author.id)
        login_datetime = datetime.fromtimestamp(login_data[1],login_timezone)
        next_login_datetime=datetime(login_datetime.year,login_datetime.month,login_datetime.day,tzinfo=login_timezone)+timedelta(1)
        #if now.timestamp()-login_data[1] >= 86400:  # 最終ログインから24時間
        login_const = 15
        if next_login_datetime <= now:# or True:
            count=login_data[0]%login_const+1
            image = cv2.imread("../assets/back.jpg")
            for y in range(3):
                for x in range(5):
                    cv_overlay_image = cv2.imread(df[x+5*y]["img"], cv2.IMREAD_UNCHANGED)  # IMREAD_UNCHANGEDを指定しα込みで読み込む
                    cv_overlay_image = cv2.resize(cv_overlay_image, (140, 140))
                    image = overlay(image, cv_overlay_image, (215+255*x, 270+255*y))
                    if count>x+5*y:
                        cv_overlay_image = cv2.imread("../assets/received.png", cv2.IMREAD_UNCHANGED)  # IMREAD_UNCHANGEDを指定しα込みで読み込む
                        cv_overlay_image = cv2.resize(cv_overlay_image, (200, 200))
                        image = overlay(image, cv_overlay_image, (188+254*x, 240+255*y))
                    img_pil = Image.fromarray(image)
                    draw = ImageDraw.Draw(img_pil)
                    draw.text((350+255*x, 400+255*y), str(df[x+5*y]["reward"]), font=ImageFont.truetype('../assets/HGRPP1.TTC', 64), fill = (256-150*(count>x+5*y),)*3+(0,))
                    image = np.array(img_pil)
            _,img=cv2.imencode(".jpg",image,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
            db.player.login.do(ctx.author.id, now.timestamp())
            f = File(fp=io.BytesIO(img),filename="login_image.jpg")
            login_bonus = df[login_data[0]%login_const]
            if login_bonus["item_id"]=="FG":
                db.player.money.add(ctx.author.id,login_bonus["reward"])
                e = Embed(title="【ログインボーナス】",description="{0}は{1}FG手に入れた。".format(ctx.author.mention,login_bonus["reward"]))
            else:
                item.obtain_an_item(ctx.author.id, login_bonus["item_id"], login_bonus["reward"])
                e = Embed(title="【ログインボーナス】",description="{0}は{1}を{2}個手に入れた。".format(ctx.author.mention,item.items.get(str(login_bonus["item_id"]),{"name": "unknown"})["name"],login_bonus["reward"]))
            e.set_image(url="attachment://login_image.jpg")
            await ctx.send(file=f, embed=e)

    @c.command(pass_context=True, description='仮実装のloginコマンド。実行はしないほうがいいかもな')
    async def login(self, ctx):
        login_timezone = timezone(timedelta(hours=+0), 'UTC')
        # login_timezone = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(login_timezone)
        login_data = db.player.login.get(ctx.author.id)
        login_datetime = datetime.fromtimestamp(login_data[1], login_timezone)
        next_login_datetime=datetime(login_datetime.year,login_datetime.month,login_datetime.day,tzinfo=login_timezone)+timedelta(1)
        #if now.timestamp()-login_data[1] >= 86400:  # 最終ログインから24時間
        if next_login_datetime > now:
            await ctx.send("あなたはすでにログインしています\n最終ログイン："+login_datetime.isoformat(sep=' ')+"\n次回ログイン可能："+next_login_datetime.isoformat(sep=' '))


def setup(bot):
    bot.add_cog(Cog(bot))
