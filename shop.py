import os
import json
from random import choice
import random
import time
import functools
from datetime import datetime, timedelta
import datetime
import logging
import requests
import json
from datetime import datetime, timedelta


# MessageHandler, filters
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.chat import Chat
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, utils
from lootcrate import LootCrates


def keystoint(x):
    return {int(k): v for k, v in x.items()}


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


class Shop:
    def __init__(self, promotion_access_filename, helpers, lootcrates, addWinner, promotion_rating):
        self.promotion_access_filename = promotion_access_filename
        self.promotion_rating = promotion_rating
        try:
            with open(promotion_access_filename, 'r') as f:
                filedata = f.read()
                self.data = json.loads(filedata, object_hook=keystoint)
        except:
            self.data = {}

        try:
            with open(promotion_rating, 'r') as f:
                filedata = f.read()
                self.rating = json.loads(filedata, object_hook=keystoint)
        except:
            self.rating = {}
        self.helpers = helpers
        self.lootcrates = lootcrates
        self.addWinnder = addWinner

    def commit(self):
        with open(self.promotion_access_filename, "w") as f:
            f.write(json.dumps(self.data))

# copypaste from lootrcates

    def addRating(self, chatId, userId, ratingId, count):
        chat = self.rating.get(chatId)
        if(chat is None):
            self.rating[chatId] = {ratingId: {userId: 0}}
        elif self.rating[chatId].get(ratingId) is None:
            self.rating[chatId][ratingId] = {userId: 0}

        if(self.rating[chatId][ratingId].get(userId) is None):
            self.rating[chatId][ratingId][userId] = count
        else:
            self.rating[chatId][ratingId][userId] += count
        self.commitRating()

    def commitRating(self):
        with open(self.promotion_rating, "w") as f:
            f.write(json.dumps(self.rating))

    def getPromoRating(self, chatId, ratingId):
        try:
            result = {}
            for user, count in self.rating[chatId][ratingId].items():
                if(count > 0):
                    result[user] = count
            return result
        except:
            pass

        return None

    def addUser(self, chatId, userId):
        chat = self.data.get(chatId)
        if(chat is None):
            self.data[chatId] = [userId]
        else:
            self.data[chatId].append(userId)
        self.commit()

    def checkAcess(self, chatId, userId):
        chat = self.data.get(chatId)
        print(self.data)
        if(chat is None):
            return False
        if(userId in self.data[chatId]):
            return True
        return False

    def buyPromoAccess(self, bot, update):
        query = update.callback_query
        chatId = query.message.chat_id
        userId = query.from_user.id
        if(self.checkAcess(chatId, userId)):
            bot.sendMessage(chat_id=chatId, text="Доступ уже приобрeтен!")
            return
        if(self.lootcrates.rmLootCrate(chatId, userId, 1, 4)):
            self.addUser(chatId, userId)
            self.commit()
            bot.sendMessage(chat_id=chatId, text="Доступ открыт!")
            bot.sendMessage(
                chat_id=chatId, text="https://cs9.pikabu.ru/post_img/big/2017/11/07/12/1510085838123685621.jpg")
        else:
            bot.sendMessage(
                chat_id=chatId, text="Недостаточно денег :(")

    def promoInfo(self, bot, update):
        query = update.callback_query
        chatId = query.message.chat_id
        bot.sendMessage(
            chat_id=chatId, text=self.helpers["promo"], parse_mode='html')

    def buyLegend(self, bot, update):
        query = update.callback_query
        chatId = query.message.chat_id
        userId = query.from_user.id
        if(self.haveMoney(20, chatId, userId)):
            self.lootcrates.rmLootCrate(chatId, userId, 1, 20)
            self.addWinnder(chatId, userId)
            bot.send_message(
                chat_id=chatId, text="Поздравляем с приобретением легенды!")
        else:
            bot.sendMessage(
                chat_id=chatId, text="Недостаточно денег :(", parse_mode='html')

    def haveMoney(self, count, chatId, userId):
        return self.lootcrates.getBalance(chatId, userId) >= count

    def getMenu(self, chatId, userId, bot):
        button_list = [
            InlineKeyboardButton("LEGEND 20 points",
                                 callback_data="buy_legend"),
            InlineKeyboardButton(
                "Alco access 4 points", callback_data="aclo_access"),
            InlineKeyboardButton("Promo info", callback_data="promo")]
        reply_markup = InlineKeyboardMarkup(
            build_menu(button_list, n_cols=2))
        bot.send_message(
            chat_id=chatId, reply_markup=reply_markup, text="choose your item")

    def getPrize(self):
        random.seed(os.urandom(10))
        chance = random.randint(1, 100)
        if(chance < 15):
            return "Балтика-0", 0
        if(chance < 35):
            return "Балтика-3", 3
        if(chance < 55):
            return "Балтика-5", 5
        if(chance < 75):
            return "Балтика-7", 7
        if(chance < 95):
            return "Балтика-9", 9
        return "ягерь!", 35
