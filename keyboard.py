import json
import sqlite3

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

import scriptForFile


guest_menu_dict = {
    'activate':'Activate📜',
    'support':'Support🆘',
    'channel':'Channel💼'
}
main_menu_dict={
    'store':'Store🛒',
    'wallet':'Wallet💵',
    'rules':'Rules🛡️',
    'channel':'Channel📰',
    'support':'Support☎️',
    'ticket':'Refund🎟️',
    'sellerProfile':'My page👤️',
}

# button_dict = {
#     'back':'back',
#     'discount':'Discount',
#     'paymethod':'Payment Method',
#     'deliverAddress':'Delivery Address',
#     'deliveryMethod':'Delivery Method',
#     'buy':'Checkout'
# }

async def guest_menu():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text=guest_menu_dict["activate"],callback_data="chooseActivateBot"))
    mark.add(InlineKeyboardButton(text=guest_menu_dict["support"],callback_data="supportGuest"))
    mark.add(InlineKeyboardButton(text=guest_menu_dict["channel"],callback_data="channelGuest"))
    return mark


async def iPaidActivation(paymentID):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="I paid!",callback_data=f"payActivate:{paymentID}"))
    mark.add(InlineKeyboardButton(text="Back", callback_data="mainMenuGuest"))
    return mark



async def checkGuestPayment(paymentID):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Check",callback_data=f"checkGuestPayment:{paymentID}"))
    mark.add(InlineKeyboardButton(text="Back",callback_data="mainMenuGuest"))
    return mark

async def mainMenuGuest():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Back", callback_data="mainMenuGuest"))
    return mark

async def mainMenu(seller = False):
    mark = InlineKeyboardMarkup()
    if seller:
        mark.add(InlineKeyboardButton(text=main_menu_dict["sellerProfile"], callback_data="sellerProfile"))
    mark.add(InlineKeyboardButton(text="Search for a BIN", callback_data=f"searchingBin"))
    mark.add(InlineKeyboardButton(text=main_menu_dict["store"], callback_data="store"),
             InlineKeyboardButton(text=main_menu_dict["wallet"], callback_data="customerWallet"))
    mark.add(InlineKeyboardButton(text="Cart🧺",callback_data="cart")),
    mark.add(InlineKeyboardButton(text=main_menu_dict["rules"], callback_data="rules"),
             InlineKeyboardButton(text=main_menu_dict["channel"], callback_data="channel"))
    mark.add(InlineKeyboardButton(text=main_menu_dict["support"], callback_data="support"),
             InlineKeyboardButton(text=main_menu_dict["ticket"], callback_data="refund"))

    return mark

seller_dict = {
    "withdraw":"Withdraw money💵",
    "insertProducct":"➕ Product",
    "deleteProducct":"➖ Product",
    "mainMenu":"Main menu⏮️"

}



async def sellerPage():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text=seller_dict["withdraw"],callback_data="withdrawSeller"))
    mark.add(InlineKeyboardButton(text=seller_dict["insertProducct"],callback_data="insertProduct"))
    mark.add(InlineKeyboardButton(text=seller_dict["deleteProducct"],callback_data="decreaseProduct"))
    mark.add(InlineKeyboardButton(text=seller_dict["mainMenu"],callback_data="sellerMainMenu"))
    return mark





async def cancelSeller():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton("Cancel",callback_data="sellerProfile"))
    return mark


async def withdrawedMoneyToSeller(payID):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="I paid!",callback_data=f"paySeller:{payID}"))
    mark.add(InlineKeyboardButton(text="Cancel",callback_data=f"withdrawRequests"))

    return mark
category_dict = {
    "spammed":"📱 Spammed",
    "sniffed":"👃 Sniffed",
    "stock":"💳 All Stock",
    "services":"📑 Services",
    "preOrder":"🏦 Pre-order BINS",
}

async def insertChooseCategory(categories):
    mark = InlineKeyboardMarkup()
    for category in categories:
        mark.add(InlineKeyboardButton(text=category[1],callback_data=f"category:{category[0]}"))
    mark.add(InlineKeyboardButton("Cancel", callback_data="superadmin"))
    return mark


async def showDeleteProduct(products):
    mark = InlineKeyboardMarkup()
    for product in products:
        for key,value in product.items():
            fileCount = scriptForFile.countCC(f"src/{value[1]}")
            mark.add(InlineKeyboardButton(text=f"{value[0][1]} | {value[0][2]} | {value[0][3]} | ({fileCount})",
                                          callback_data=f"deleteBase:{value[1]}"))
    mark.add(InlineKeyboardButton("Cancel",callback_data="sellerProfile"))
    return mark

# eth, usdt, btc, Ltc


crypto_dict = {
    "btc":"Bitcoin",
    "usdt":"Usdt",
    "eth":"Ethereum",
    "ltc":"Litecoin"
}

async def chooseActivationCrypto():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text=crypto_dict["btc"],callback_data="activateBot:btc"))
    mark.add(InlineKeyboardButton(text=crypto_dict["usdt"],callback_data="activateBot:usdttrc20"))
    mark.add(InlineKeyboardButton(text=crypto_dict["eth"],callback_data="activateBot:eth"))
    mark.add(InlineKeyboardButton(text=crypto_dict["ltc"],callback_data="activateBot:ltc"))
    mark.add(InlineKeyboardButton(text="Back",callback_data="mainMenuGuest"))
    return mark
async def chooseDepositCrypto():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text=crypto_dict["btc"],callback_data="topup:btc"))
    mark.add(InlineKeyboardButton(text=crypto_dict["usdt"],callback_data="topup:usdttrc20"))
    mark.add(InlineKeyboardButton(text=crypto_dict["eth"],callback_data="topup:eth"))
    mark.add(InlineKeyboardButton(text=crypto_dict["ltc"],callback_data="topup:ltc"))
    mark.add(InlineKeyboardButton(text="Back",callback_data="sellerMainMenu"))
    return mark


async def checkDeposit(payment_id):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Check", callback_data=f"checkTopUp:{payment_id}"))
    mark.add(InlineKeyboardButton(text="New deposit",callback_data=f"newDeposit"))
    mark.add(InlineKeyboardButton(text="Back", callback_data="mainMenu"))
    return mark


async def superAdmin(active):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton("➕Category",callback_data="addCategory"))
    mark.add(InlineKeyboardButton("➖Category",callback_data="delCategory"))
    mark.add(InlineKeyboardButton("➕Base",callback_data="addBase"))
    mark.add(InlineKeyboardButton("➖Base",callback_data="delBase"))
    mark.add(InlineKeyboardButton("Edit price",callback_data="editPrice"))
    mark.add(InlineKeyboardButton("Edit baseName",callback_data="editName"))
    mark.add(InlineKeyboardButton("List of refunds",callback_data="listOfRefunds"))
    mark.add(InlineKeyboardButton(f"Buy access {'ON' if active == 1 else 'OFF'}",callback_data="changeBuyAccess"))
    mark.add(InlineKeyboardButton(f"Withdraw requets",callback_data="withdrawRequests"))
    mark.add(InlineKeyboardButton(f"Statistics",callback_data="statistics"))

    return mark


async def cancelSuperAdmin():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Cancel",callback_data="superadmin"))
    return mark

async def deleteCategory(categories):
    mark = InlineKeyboardMarkup()
    for category in categories:
        mark.add(InlineKeyboardButton(text=category[1],callback_data=f"deletingCategory:{category[0]}"))
    mark.add(InlineKeyboardButton(text="Cancel", callback_data="superadmin"))
    return mark


async def customerCategory(categories):
    mark =  InlineKeyboardMarkup()
    for category in categories:
        mark.add(InlineKeyboardButton(text=category[0],callback_data=f"customerCategory:{category[0]}"))
    mark.add(InlineKeyboardButton(text=category_dict["preOrder"],callback_data=f"preOrder"))
    mark.add(InlineKeyboardButton(text="Back", callback_data="sellerMainMenu"))
    return mark


async def customerCountry(category, countries):
    mark = InlineKeyboardMarkup()
    for country in countries:
        mark.add(InlineKeyboardButton(text=country[0],callback_data=f"customerCountry:{category}:{country[0]}"))
    mark.add(InlineKeyboardButton(text="Search for a BIN", callback_data=f"searchingBin"))
    mark.add(InlineKeyboardButton(text="Back", callback_data=f"store"))
    return mark


async def customerProducts(category,country,products):
    mark = InlineKeyboardMarkup()
    for product in products:
        mark.add(InlineKeyboardButton(text=product[1],callback_data=f"customerExactProduct:{product[0]}"))
    mark.add(InlineKeyboardButton(text="Cart🧺", callback_data="cart"))
    mark.add(InlineKeyboardButton(text="Back", callback_data=f"customerCategory:{category}"))
    return mark


async def showBins(category, country, productID, fullzs,price):
    mark = InlineKeyboardMarkup()
    for fullz in fullzs:
        for key,full in fullz.items():
            for f in full:
                if len(f[1])>3:
                    mark.add(InlineKeyboardButton(text=f"{f[1][2]} - {f[1][0]} - {f[1][1]} - £{price}",
                                      callback_data=f"addToCart:{productID}:{f[1][3]}:{key}"))
    mark.add(InlineKeyboardButton(text="Cart🧺",callback_data="cart"))
    mark.add(InlineKeyboardButton(text="Back", callback_data=f"customerCountry:{category}:{country}"))
    return mark

async def showFoundBins(fullzs):
    mark = InlineKeyboardMarkup()
    for fullz in fullzs:
        for key,f in fullz.items():
                mark.add(InlineKeyboardButton(text=f"{f['cardBIN']} - {f['DOB']} - {f['postcode']} - £{f['price']}",
                                      callback_data=f"addToCart:{f['baseID']}:{f['cardNumber']}:{key}"))
    mark.add(InlineKeyboardButton(text="Cart🧺",callback_data="cart"))
    mark.add(InlineKeyboardButton(text="Back", callback_data=f"mainMenu"))
    return mark

async def buyFullz(totalPrice):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Buy💳",callback_data=f"buyFullz:{totalPrice}"))
    mark.add(InlineKeyboardButton(text="Clean",callback_data=f"cleanCart"))
    mark.add(InlineKeyboardButton(text="Back",callback_data=f"mainMenu"))
    return mark


async def backToMainMenu():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Cancel",callback_data="mainMenu"))
    return mark


async def insertBaseCategory(categories):
    mark = InlineKeyboardMarkup()
    for category in categories:
        mark.add(InlineKeyboardButton(text=category[0],callback_data=f"insertBaseCat:{category[0]}"))
    return mark


async def insertBaseCountry(category,countries):
    mark = InlineKeyboardMarkup()
    for country in countries:
        mark.add(InlineKeyboardButton(text=f"{country[0]}",callback_data=f"insertBaseCountry:{category}:{country[0]}"))
    return mark


async def insertBaseProduct(category, country, products):
    mark = InlineKeyboardMarkup()
    for product in products:
        mark.add(InlineKeyboardButton(text=product[1], callback_data=f"insertBaseFile:{product[0]}"))
    mark.add(InlineKeyboardButton(text="Back", callback_data=f"customerCategory:{category}"))
    return mark


async def adminRefundSystem(orderID):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Download a file",callback_data=f"downloadSuperAdmin:{orderID}"))
    mark.add(InlineKeyboardButton(text="Accept",callback_data=f"decisionRefund:{orderID}:accepted"))
    mark.add(InlineKeyboardButton(text="Reject a refund",callback_data=f"decisionRefund:{orderID}:rejection"))
    return mark


async def showRefunds(refunds):
    mark = InlineKeyboardMarkup()
    for r in refunds:
        mark.add(InlineKeyboardButton(f"Order: {r[1]}",callback_data=f"showExactRefund:{r[1]}"))
    mark.add(InlineKeyboardButton(text="Cancel", callback_data="superadmin"))
    return mark


async def showRequests(withdrawRequests):
    mark = InlineKeyboardMarkup()
    for request in withdrawRequests:
        mark.add(InlineKeyboardButton(f"{request[1]}--£{request[2]}",callback_data=f"showExactRequest:{request[0]}"))
    mark.add(InlineKeyboardButton(text="Cancel", callback_data="superadmin"))
    return mark


async def newSeller(userId):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Accept✅", callback_data= f"addSeller:{userId}:1"))
    mark.add(InlineKeyboardButton(text="Decline❎", callback_data=f"addSeller:{userId}:0"))
    return mark


async def delBaseCategory(categories):
    mark = InlineKeyboardMarkup()
    for category in categories:
        mark.add(InlineKeyboardButton(text=category[0], callback_data=f"delBaseCategory:{category[0]}"))
    mark.add(InlineKeyboardButton("Cancel", callback_data="superadmin"))
    return mark


async def delBaseCountry(category,countries):
    mark = InlineKeyboardMarkup()
    for country in countries:
        mark.add(InlineKeyboardButton(text=country[0], callback_data=f"delBaseCountry:{category}:{country[0]}"))
    mark.add(InlineKeyboardButton("Cancel", callback_data="superadmin"))
    return mark


async def delBaseProduct(products):
    mark = InlineKeyboardMarkup()
    for product in products:
        mark.add(InlineKeyboardButton(text=product[3], callback_data=f"delBaseProduct:{product[0]}"))
    mark.add(InlineKeyboardButton("Cancel", callback_data="superadmin"))
    return mark


async def downloadFile(orderID):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Download a file",callback_data=f"downloadSuperAdmin:{orderID}"))
    return mark

async def backToStats():
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Back",callback_data="statistics"))
    return mark
async def showSellers(sellers):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Reset balance",callback_data="resetBalance"))
    for seller in sellers:
        if seller[0] == 777:
            pass
        else:
            mark.add(InlineKeyboardButton(text=seller[0],callback_data=f"showSeller:{seller[0]}"))
    mark.add(InlineKeyboardButton("Back", callback_data="superadmin"))
    return mark


async def deleteSeller(sellerId):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="Delete seller",callback_data=f"deleteSeller:{sellerId}"))
    mark.add(InlineKeyboardButton(text="Change percentage",callback_data=f"changePercentage:{sellerId}"))
    mark.add(InlineKeyboardButton(text="Back",callback_data="statistics"))
    return mark


async def iPaidDeposit(payment_id):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(text="I paid!",callback_data=f"payDeposit:{payment_id}"))
    mark.add(InlineKeyboardButton(text="New deposit",callback_data=f"newDeposit"))
    mark.add(InlineKeyboardButton(text="Cancel",callback_data="mainMenu"))
    return mark


async def editPrice(categories):
    mark = InlineKeyboardMarkup()
    for category in categories:
        mark.add(InlineKeyboardButton(text=category[0],callback_data=f"categoryEditPric:{category[0]}"))
    mark.add(InlineKeyboardButton("Back", callback_data="superadmin"))
    return mark


async def editPriceCountry(category, countries):
    mark = InlineKeyboardMarkup()
    for country in countries:
        mark.add(InlineKeyboardButton(text=country[0], callback_data=f"countryEditPric:{category}:{country[0]}"))
    mark.add(InlineKeyboardButton("Cancel", callback_data="superadmin"))
    return mark


async def productEditPrice(category,products):
    mark = InlineKeyboardMarkup()
    for product in products:
        mark.add(InlineKeyboardButton(text=product[3],callback_data=f"editPriceProduct:{product[0]}"))
    mark.add(InlineKeyboardButton(text="Back",callback_data=f"categoryEditPric:{category}"))
    return mark


async def nameEdit(categories):
    mark = InlineKeyboardMarkup()
    for category in categories:
        mark.add(InlineKeyboardButton(text=category[0], callback_data=f"categoryEditName:{category[0]}"))
    mark.add(InlineKeyboardButton("Back", callback_data="superadmin"))
    return mark

async def editNameCountry(category, countries):
    mark = InlineKeyboardMarkup()
    for country in countries:
        mark.add(InlineKeyboardButton(text=country[0], callback_data=f"countryEditName:{category}:{country[0]}"))
    mark.add(InlineKeyboardButton("Cancel", callback_data="superadmin"))
    return mark


async def nameEditName(category,products):
    mark = InlineKeyboardMarkup()
    for product in products:
        mark.add(InlineKeyboardButton(text=product[3],callback_data=f"nameEditName:{product[0]}"))
    mark.add(InlineKeyboardButton(text="Back",callback_data=f"categoryEditName:{category}"))
    return mark