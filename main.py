import configparser
import json
import sqlite3
import time

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputFile
from aiogram.utils import executor

import keyboard
import payment
import scriptForFile

config = configparser.ConfigParser()
config.read("settings.ini")

TOKEN = config["Basic"]["TOKEN"]

conn = sqlite3.Connection('store.db', check_same_thread=False)
cursor = conn.cursor()

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dict_message = {
    "start": """Welcome to ATLANTIS  👋
Use the menu below to interact with the bot 🤖

⚠️┇Your Account Is Not Activated 😢
⚠️┇Paid Activation is required
⚠️┇Required Amount: £50 Approximately
⚠️┇Paid amount will be credited to your account
""",
    "guest_payment": "Payment: <b>{}</b>\n\nPlease pay: <code>{}</code>\n{} address: <code>{}</code>",
    "guest_payment_usd": "Payment: <b>{}</b>\n\n<b>SEND ONLY TRC</b>\n\nPlease pay: <code>{}</code>\nUSDT address: <code>{}</code>",
    "mainMenu": """Welcome to ATLANTIS Fullz Shop! 

We aim to satisfy your needs with HQ spammed fullz and wish you the best of luck 👏🏻


Join (channel)for daily updates, all sales are strictly made on the Bot and will never PM first.
 
managed @AtlantisSupporting""",
    "rules":"""Refund Policy:

IF YOU FAIL TO FOLLOW OUR CLEAR INSTRUCTED RULES YOU WILL NOT BE REFUNDED. 

How to Apply for a Refund: 

 1. Check card on pay.google.com 

 2. If the card is dead, click refund at the bottom of purchased card. 

 3. Send the support account a Screenshot/Photo that proves the card is dead make sure to include the fullz id.

4. When checking card on pay.google.com, you have an automatic 3 minute timer. 

5. Failing to check card / provide proof of card being dead past the 3 minute timer can result in no refund. 

6. When providing a photo or a screenshot, please make sure: Card Number, Expiry Date and CCV are fully visible.

7. If number doesn't call or is invalid this doesn't qualify for refund /unless all missing or fake info.

 8. If all the details are valid and the card is dead your account will be credited again with a refund within 5 minutes


Keep in Mind: 

(£10 & £5 BASES ARE NOT REFUNDABLE) 

(HSBC CARDS ARE NOT REFUNDABLE
Or ANY company under them such as John lewis,M&S, First direct ,etc)

⛔️ NOTE ⛔️ 

🔹Support account is available 24/7 @AtlantisSupporting.

🔹1 Transaction per wallet unless payment is underpaid. Our wallet always changes after each completed deposit. 

🔹Payment CRYPTO ONLY 

🔹 BY PURCHASING YOU AGREE TO THESE RULES. FAILURE TO READ THEM WILL FORFEIT YOUR REFUND / REPLACEMENT. WE SHALL GIVE NO WARNINGS""",
    "channelText":"https://t.me/+HGbnvhM_N_owNzM0",
    "supportText":"Dm @AtlantisSupporting",
}





@dp.message_handler(commands=["start", "menu"], state='*')
async def start(message: types.Message, state: FSMContext):
    reply_markup = {"inline_keyboard": [[{"text": "aa", "callback_data": "aa"}]]}
    await state.reset_state()
    cursor.execute("SELECT active FROM status WHERE name =?", ("guestPayment",))
    guestPaymentStatus = cursor.fetchone()
    cursor.execute("SELECT id FROM sellers where user_id = ?", (message.from_user.id,))
    sellerExists = cursor.fetchone()
    cursor.execute("SELECT id FROM users where user_id = ?", (message.from_user.id,))
    userExists = cursor.fetchone()
    if guestPaymentStatus[0] == 1:
        if userExists:
            await message.answer(dict_message["mainMenu"], reply_markup=await keyboard.mainMenu(True if sellerExists else False))
        else:
            await message.answer(dict_message["start"], reply_markup=await keyboard.guest_menu())
    else:
        if userExists:
            await message.answer(dict_message["mainMenu"], reply_markup=await keyboard.mainMenu(True if sellerExists else False))
        else:
            try:
                cursor.execute("INSERT INTO users (user_id,balance) VALUES (?,?)", (message.from_user.id, 0,))
                conn.commit()
            except:
                pass
            await message.answer(dict_message["mainMenu"], reply_markup=await keyboard.mainMenu())


@dp.callback_query_handler(lambda message: message.data == 'mainMenu')
async def callStart(call: types.CallbackQuery):
    cursor.execute("SELECT id FROM sellers where user_id = ?", (call.from_user.id,))
    userExists = cursor.fetchone()
    await call.message.edit_text(dict_message["mainMenu"], reply_markup=await keyboard.mainMenu(True if userExists else False))

@dp.callback_query_handler(lambda message: message.data == 'mainMenuGuest')
async def callStart(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.message.edit_text(dict_message["start"], reply_markup=await keyboard.guest_menu())


@dp.callback_query_handler(lambda message: message.data == 'rules')
async def callStart(call: types.CallbackQuery):
    await call.message.edit_text(dict_message["rules"],reply_markup=await keyboard.backToMainMenu())



@dp.callback_query_handler(lambda message: message.data == 'channel')
async def callStart(call: types.CallbackQuery):
    await call.message.edit_text(dict_message["channelText"],reply_markup=await keyboard.backToMainMenu())



@dp.callback_query_handler(lambda message: message.data == 'support')
async def callStart(call: types.CallbackQuery):
    await call.message.edit_text(dict_message["supportText"],reply_markup=await keyboard.backToMainMenu())


@dp.callback_query_handler(lambda message: message.data == 'channelGuest')
async def callStart(call: types.CallbackQuery):
    await call.message.edit_text(dict_message["channelText"],reply_markup=await keyboard.mainMenuGuest())



@dp.callback_query_handler(lambda message: message.data == 'supportGuest')
async def callStart(call: types.CallbackQuery):
    await call.message.edit_text(dict_message["supportText"],reply_markup=await keyboard.mainMenuGuest())

#Got it friend? yes now look 



@dp.callback_query_handler(lambda message: message.data == 'sellerMainMenu')
async def callStart(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    cursor.execute("SELECT id FROM sellers where user_id = ?", (call.from_user.id,))
    userExists = cursor.fetchone()
    await call.message.edit_text(dict_message["mainMenu"],
                                 reply_markup=await keyboard.mainMenu(True if userExists else False))


@dp.callback_query_handler(lambda message: message.data == 'chooseActivateBot')
async def paymentPage(call: types.CallbackQuery):
    cursor.execute("SELECT * FROM deposits WHERE user_id = ? and status = ?",(call.from_user.id,0,))
    payData = cursor.fetchone()
    if payData:
        paymentID = payData[2]
        status,address,pay_amount,crypto,price_amount = payment.checkPayment(paymentID)
        await call.message.edit_text(
            text=dict_message["guest_payment_usd"].format(paymentID, round(pay_amount, 5), address) if crypto == "usdt"
            else dict_message["guest_payment"].format(paymentID, round(pay_amount, 5), crypto.upper(), address),
            parse_mode="HTML",
            reply_markup=await keyboard.checkGuestPayment(paymentID))
    else:
        await call.message.edit_text("Choose crypto", reply_markup=await keyboard.chooseActivationCrypto())

#
@dp.callback_query_handler(text_contains = 'activateBot')
async def paymentPage(call: types.CallbackQuery):
    crypto = call.data.split(":")[1]
    await call.message.edit_text("Wait getting address...")
    address, paymentID, pay_amount = payment.createTopUp(50, crypto, call.from_user.id, )

    if address:
        await call.message.edit_text(text=dict_message["guest_payment_usd"].format(paymentID, round(pay_amount, 5), address) if crypto=="usdt"
        else dict_message["guest_payment"].format(paymentID, round(pay_amount, 5),crypto.upper(), address),
                                 parse_mode="HTML",
                                 reply_markup=await keyboard.iPaidActivation(paymentID))
    else:
        await call.answer("This crypto not available, try later or another",show_alert=True)
        await call.message.edit_text("Choose crypto", reply_markup=await keyboard.chooseActivationCrypto())


@dp.callback_query_handler(text_contains = 'payActivate')
async def paymentPage(call: types.CallbackQuery):
    paymentID = call.data.split(":")[1]
    cursor.execute("INSERT INTO deposits (user_id,paymentID,status) VALUES (?,?,?)", (call.from_user.id,
                                                                                      paymentID,
                                                                                      0))
    conn.commit()
    await call.message.edit_reply_markup(await keyboard.checkGuestPayment(paymentID))



# @dp.callback_query_handler(text_contains = 'activateBot')
# async def paymentPage(call: types.CallbackQuery):
#     crypto = call.data.split(":")[1]
#     await call.message.edit_text("Wait getting address...")
#     address,paymentID, pay_amount = payment.createTopUp(20, crypto, call.from_user.id,)
#     if address:
#         await call.message.edit_text(text=dict_message["guest_payment_usd"].format(paymentID, round(pay_amount, 5), address) if crypto=="usdt"
#         else dict_message["guest_payment"].format(paymentID, round(pay_amount, 5),crypto.upper(), address),
#                                  parse_mode="HTML",
#                                  reply_markup=await keyboard.iPaidActivation(paymentID))
#     else:
#         await call.answer("This crypto not available, try later or another",show_alert=True)
#         await call.message.edit_text("Choose crypto", reply_markup=await keyboard.chooseActivationCrypto())




@dp.callback_query_handler(text_contains='checkGuestPayment')
async def checkPayment(call: types.CallbackQuery):
    paymentID = call.data.split(":")[1]
    status = payment.checkPayment(paymentID)[0]
    await call.message.edit_reply_markup(None)
    time.sleep(1)
    if status == "waiting":
        await call.answer("Funds have not yet been received", show_alert=True)
        await call.message.edit_reply_markup(await keyboard.checkGuestPayment(paymentID))
    elif status == "confirming":
        await call.answer("Funds is confirming!", show_alert=True)
        await call.message.edit_reply_markup(await keyboard.checkGuestPayment(paymentID))
    elif status in ["confirmed", 'sending', 'finished']:
        try:
            cursor.execute("INSERT INTO users (user_id,balance) VALUES (?,?)", (call.from_user.id, 0,))
            conn.commit()
        except:
            pass
        cursor.execute("UPDATE users SET balance = balance+? where user_id = ?",
                       (50, call.from_user.id,))
        cursor.execute("UPDATE deposits SET status = 1 where user_id = ?",
                       (call.from_user.id,))

        conn.commit()
        await call.answer("Paid!", show_alert=True)
        cursor.execute("SELECT id FROM sellers where user_id = ?", (call.from_user.id,))
        userExists = cursor.fetchone()

        await call.message.edit_text(dict_message["mainMenu"],
                                     reply_markup=await keyboard.mainMenu(True if userExists else False))
    elif status == 'failed':
        await call.answer("Something went wrong, text to admins".upper(), show_alert=True)
        await call.message.edit_reply_markup(await keyboard.checkGuestPayment(paymentID))







############### INSERTING files to BIN


@dp.callback_query_handler(lambda message: message.data == 'insertProduct')
async def paymentPage(call: types.CallbackQuery):
    cursor.execute("SELECT category FROM products GROUP BY category")
    categories = cursor.fetchall()
    await call.message.edit_text("Choose category",reply_markup=await keyboard.insertBaseCategory(categories))

@dp.callback_query_handler(text_contains='insertBaseCat')
async def customerStoreCountry(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    cursor.execute("SELECT country FROM products WHERE category = ? GROUP BY country", (category,))
    countries = cursor.fetchall()
    await call.message.edit_text("Choose country",
                                 reply_markup=await keyboard.insertBaseCountry(category, countries))

@dp.callback_query_handler(text_contains='insertBaseCountry')
async def customerStoreProduct(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    country = call.data.split(":")[2]
    cursor.execute("SELECT id,name FROM products WHERE category = ? and country = ?", (category, country,))
    products = cursor.fetchall()
    await call.message.edit_text("Choose BASE",
                                 reply_markup=await keyboard.insertBaseProduct(category, country, products))


class Uploader(StatesGroup):
    file = State()

@dp.callback_query_handler(text_contains='insertBaseFile')
async def customerStoreProduct(call: types.CallbackQuery,state:FSMContext):
    productID = call.data.split(":")[1]
    await call.message.edit_text("Send fullz file",
                                 reply_markup=None)
    await state.update_data(mid = call.message.message_id,productID=productID)
    await Uploader.file.set()



# @dp.message_handler(content_types=["document"], state=Base.file)
# async def insertProductFile(message: types.Message, state: FSMContext):
#
#     await bot.edit_message_text(chat_id=message.from_user.id,
#                                 message_id=data["mid"],
#                                 text=f"Category: <b>{data['categoryName']}</b>\n"
#                                      f"Country: <b>{data['country']}</b>\n"
#                                      f"Name: <b>{data['name']}</b>\n"
#                                      f"Price: <b>{data['price']}$</b>\n"
#                                      f"File: ✅\n\n"
#                                      f"Product was uploaded",
#                                 parse_mode="HTML", reply_markup=await keyboard.cancelSeller())
#     await state.finish()


@dp.message_handler(content_types=["document"],state=Uploader.file)
async def insertProductCategory(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    fileName = f"{message.from_user.id}/{int(time.time())}.txt"
    await message.document.download(destination_file=f"src/{fileName}")
    cursor.execute("INSERT INTO bases(baseID,pathFile,seller_id) VALUES (?,?,?)",
                   (data['productID'], fileName, message.from_user.id,))
    conn.commit()
    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=data["mid"],
                                text="Fullz was added!",reply_markup=await keyboard.cancelSeller())
    await state.finish()
###############Searching BIN

class Search(StatesGroup):
    bin = State()


@dp.callback_query_handler(lambda message: message.data == 'searchingBin')
async def searchingBIN(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Write BIN to search")
    await state.update_data(mid = call.message.message_id)
    await Search.bin.set()


@dp.message_handler(state=Search.bin)
async def insertProductCategory(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit() and len(message.text)==6:

        cursor.execute("SELECT * FROM bases")
        baseInfo = cursor.fetchall()
        foundBaseId = []
        for base in baseInfo:
            getExistsID = scriptForFile.searchBin(f"src/{base[2]}",message.text)
            if getExistsID:
                foundBaseId.append({base[0]:getExistsID})
        if foundBaseId:
            await message.delete()
            fullFullz = []
            for file in foundBaseId:
                for key, binID in file.items():
                    for id in binID:
                        cursor.execute("SELECT pathFile,baseID FROM bases WHERE id = ?",(key,))
                        filePathBaseID = cursor.fetchone()
                        filePath = filePathBaseID[0]
                        baseID = filePathBaseID[1]
                        cursor.execute("SELECT price FROM products WHERE id = ?",(baseID,))
                        price = cursor.fetchone()
                        fullzs = scriptForFile.getExactlyId(id,f"src/{filePath}")
                        fullzs['baseID'] = baseID
                        fullzs['price'] = price[0]
                        fullFullz.append({key:fullzs})
            await bot.edit_message_text(chat_id=message.from_user.id,message_id=data["mid"],
                                        text="BIN - Birth year - Postcode - Price",
                                                     reply_markup=await keyboard.showFoundBins(fullFullz
                                                                                          ))
            await state.finish()
        else:
                await message.delete()
                await bot.edit_message_text(chat_id=message.from_user.id,
                                            message_id=data["mid"],
                                            text="No BINs",reply_markup=await keyboard.backToMainMenu())
                await state.finish()
    else:

        await message.delete()
        await bot.edit_message_text(chat_id=message.from_user.id,
                                    message_id=data["mid"],
                                    text="Write only 6 digits",)
        await Search.bin.set()

###############


###########BECOME A SELLER

@dp.message_handler(commands=["becomeseller"], state='*')
async def becomeSeller(message: types.Message, state: FSMContext):
    if message.from_user.username:
        cursor.execute("SELECT * FROM sellers WHERE user_id = ?",(message.from_user.id,))
        userExists = cursor.fetchone()
        if not userExists:
            for admin in admins:
                await bot.send_message(chat_id=admin,
                                       text="New seller!\n"
                                            f"UserID:<b>{message.from_user.id}</b>\n"
                                            f"Username:@{message.from_user.username}",parse_mode="html",
                                       reply_markup=await keyboard.newSeller(message.from_user.id))
            await message.answer("Your request was sent to administrator.\nSoon you get answer",
                                 reply_markup=await keyboard.backToMainMenu())
        else:
            await message.answer("You are already seller",reply_markup=await keyboard.cancelSeller())

    else:
        await message.answer("Set a username, try again!",reply_markup=await keyboard.backToMainMenu())




@dp.callback_query_handler(text_contains='addSeller')
async def customerStoreCountry(call: types.CallbackQuery):
    sellerID = call.data.split(":")[1]
    decision = call.data.split(":")[2]
    userInfo = await bot.get_chat_member(int(sellerID),int(sellerID))
    username = userInfo.user["username"]
    if int(decision) == 1:
        try:
            cursor.execute("INSERT INTO sellers(user_id,balance) VALUES (?,?)",(sellerID,0,))
            cursor.execute("INSERT INTO userPercentage(user_id,percentage) VALUES (?,?)",(sellerID,70,))
            conn.commit()
            await bot.send_message(chat_id=sellerID,text="Congratulations!\nNow you are seller",reply_markup=await keyboard.mainMenu(True))
        except:
            pass
        await call.message.edit_text(text="New seller!\n"
                                          f"UserID:<b>{sellerID}</b>\n"
                                          f"Username:@{username}\n"
                                          f"Accepted✅",parse_mode="html", reply_markup=await keyboard.cancelSuperAdmin())


    else:
        await bot.send_message(chat_id=sellerID,text="Sorry your request to become a seller declined.\nTry again later!",
                               reply_markup=await keyboard.backToMainMenu())
        await call.message.edit_text(text="New seller!\n"
                                        f"UserID:<b>{sellerID}</b>\n"
                                        f"Username:@{username}\n"
                                          f"Declined❎",parse_mode="html",reply_markup=await keyboard.cancelSuperAdmin())



    ############

############### REFUND

class Refund(StatesGroup):
    orderID = State()


@dp.callback_query_handler(lambda message: message.data == 'refund')
async def callStart(call: types.CallbackQuery,state:FSMContext):
    await call.message.edit_text("Send your order ID to get refund")
    await state.update_data(mid = call.message.message_id)
    await Refund.orderID.set()



@dp.message_handler(state=Refund.orderID)
async def insertProductCategory(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit():
        cursor.execute("SELECT * FROM sales WHERE id = ? and buyer_id = ?",(message.text,
                                                                            message.from_user.id,))
        orderExists = cursor.fetchone()
        if orderExists:
            cursor.execute("SELECT id FROM refund WHERE orderID = ?",(message.text,))
            refundExists = cursor.fetchone()
            if not refundExists:
                for admin in admins:
                    await bot.send_message(chat_id=admin, text="New refund",
                                           reply_markup=await keyboard.adminRefundSystem(message.text))
                cursor.execute("SELECT percentage FROM userPercentage WHERE user_id=?", (orderExists[4],))
                percentage = cursor.fetchone()
                price = orderExists[3]
                sellerSold = scriptForFile.percentage(price, percentage[0])
                cursor.execute("INSERT into refund (orderID,user_id,price) VALUES (?,?,?)",(message.text,
                                                                                    orderExists[4],sellerSold,))
                conn.commit()
                await bot.edit_message_text(chat_id=message.from_user.id,
                                        message_id=data["mid"], text='Returning verification')
            else:
                await bot.edit_message_text(chat_id=message.from_user.id,
                                            message_id=data["mid"], text='You got refund for this order')
        else:
            await bot.edit_message_text(chat_id=message.from_user.id,
                                        message_id=data["mid"], text='You dont have this order')
        await state.finish()
    else:
        await bot.edit_message_text(chat_id=message.from_user.id,
                                    message_id=data["mid"],text="Write digits")
    await message.delete()
###############
###############CUSTOMER


@dp.callback_query_handler(lambda message: message.data == 'store')
async def customerStoreCategory(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("SELECT category FROM products GROUP BY category")
    categories = cursor.fetchall()
    await call.message.edit_text("--- MAIN MENU ---", reply_markup=await keyboard.customerCategory(categories))



@dp.callback_query_handler(text_contains='customerCategory')
async def customerStoreCountry(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    cursor.execute("SELECT country FROM products WHERE category = ? GROUP BY country", (category,))
    countries = cursor.fetchall()
    await call.message.edit_text("Choose country",
                                 reply_markup=await keyboard.customerCountry(category, countries))


@dp.callback_query_handler(text_contains='customerCountry')
async def customerStoreProduct(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    country = call.data.split(":")[2]
    cursor.execute("SELECT id,name FROM products WHERE category = ? and country = ?", (category, country,))
    products = cursor.fetchall()
    await call.message.edit_text("Choose product",
                                 reply_markup=await keyboard.customerProducts(category, country, products))


@dp.callback_query_handler(text_contains='customerExactProduct')
async def customerStoreProduct(call: types.CallbackQuery):
    productID = call.data.split(":")[1]
    cursor.execute("SELECT category,country,price FROM products WHERE id = ?", (productID,))
    categoryCountryPrice = cursor.fetchone()
    cursor.execute("SELECT id,pathFile FROM bases WHERE baseID = ?",(productID))
    pathFile = cursor.fetchall()
    print(pathFile)
    fullFullz = []
    for path in pathFile:
        fullzs = scriptForFile.getExactlyBin(f"src/{path[1]}")
        fullFullz.append({path[0]:fullzs})
    await call.message.edit_text("BIN - Birth year - Postcode - Price",
                                 reply_markup=await keyboard.showBins(categoryCountryPrice[0], categoryCountryPrice[1],
                                                                      productID, fullFullz,categoryCountryPrice[2]))


@dp.callback_query_handler(text_contains='addToCart')
async def customerStoreProduct(call: types.CallbackQuery):
    productID = call.data.split(":")[1]
    cardNumber = call.data.split(":")[2]
    fileID = call.data.split(":")[3]
    cursor.execute("SELECT * FROM cart WHERE user_id = ? and fileID=? and cardNumber = ?", (call.from_user.id,
                                                                               int(fileID), int(cardNumber),))
    cartExists = cursor.fetchone()
    if cartExists:
        await call.answer("Products exists in cart!", show_alert=True)
    else:
        cursor.execute("INSERT INTO cart (user_id,productID,cardNumber,fileID) VALUES (?,?,?,?)",
                       (call.from_user.id, productID, cardNumber,fileID))
        conn.commit()
        await call.answer("Record added", show_alert=True)


@dp.callback_query_handler(text_contains='cart')
async def customerCart(call: types.CallbackQuery):
    text = "Your cart\n\nBirth year | Postcode | BIN\n*********"
    price = 0
    cursor.execute("SELECT * FROM cart WHERE user_id=?", (call.from_user.id,))
    productBinID = cursor.fetchall()
    if productBinID:
        for id in productBinID:
            cursor.execute("SELECT * FROM products WHERE id = ?",(id[2],))
            product = cursor.fetchone()
            cursor.execute("SELECT pathFile FROM bases WHERE id = ?",(id[4],))
            pathFile = cursor.fetchone()
            exactIdByCardNumber = scriptForFile.getExactlyIdByCardNumber(f"src/{pathFile[0]}",id[3])
            productData = scriptForFile.getExactlyId(exactIdByCardNumber,f"src/{pathFile[0]}")
            price += product[4]
            text += f"\n{productData['DOB']} | {productData['postcode']} | {productData['cardBIN']}"
        await call.message.edit_text(f"{text}\n*********\nTotal price £<b>{price}</b>",parse_mode="HTML",
                                     reply_markup=await keyboard.buyFullz(price))
    else:
        await call.answer("Cart is empty!",show_alert=True)


@dp.callback_query_handler(text_contains = 'buyFullz')
async def buyingFullz(call: types.CallbackQuery):
    totalPrice = call.data.split(":")[1]
    cursor.execute("SELECT balance FROM users WHERE user_id = ?",(call.from_user.id,))
    balance = cursor.fetchone()
    if balance[0] >= int(totalPrice):

        cursor.execute("SELECT * FROM cart WHERE user_id=?", (call.from_user.id,))
        productBinID = cursor.fetchall()
        await call.message.edit_text("Sending!")
        for id in productBinID:
            cursor.execute("SELECT * FROM products WHERE id = ?",(id[2],))
            product = cursor.fetchone()
            price = product[4]
            cursor.execute("SELECT * FROM bases WHERE id = ?", (id[4],))
            baseInfo = cursor.fetchone()
            filePath = f"src/{baseInfo[2]}"
            exactIdByCardNumber = scriptForFile.getExactlyIdByCardNumber(filePath, id[3])

            sendFileName = scriptForFile.buyExactlyId(filePath,exactIdByCardNumber,call.from_user.id)
            cursor.execute("INSERT INTO sales (product,buyer_id,price,seller_id,pathFile,dates) VALUES (?,?,?,?,?,CURRENT_DATE)",
                           (f"{product[2]}--{product[3]}", call.from_user.id, price, baseInfo[3],sendFileName,))
            lastOrderID = cursor.lastrowid

            cursor.execute("SELECT percentage FROM userPercentage WHERE user_id=?", ( baseInfo[3],))
            percentage = cursor.fetchone()
            sellerSold = scriptForFile.percentage(price, percentage[0])
            cursor.execute("Update sellers SET balance = balance + ? WHERE user_id = ?",
                           (round(sellerSold,1), baseInfo[3],))
            conn.commit()
            cursor.execute("Update sellers SET balance = balance + ? WHERE user_id = ?",
                           (round(price - sellerSold,1), 777,))
            conn.commit()
            scriptForFile.removeRecord(exactIdByCardNumber,filePath)
            await bot.send_document(call.from_user.id,InputFile(sendFileName),
                                    caption=f"Order id: <b>{lastOrderID}</b>",parse_mode="HTML")
            time.sleep(2)
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id =?",
                       (totalPrice,call.from_user.id,))
        cursor.execute("DELETE FROM cart")
        conn.commit()
        cursor.execute("SELECT id FROM sellers where user_id = ?", (call.from_user.id,))
        userExists = cursor.fetchone()
        await call.message.edit_text("Done!")
        await call.message.answer(dict_message["mainMenu"],
                                     reply_markup=await keyboard.mainMenu(True if userExists else False))

    else:
        await call.answer("Not enough funds to buy")
###Переделать отправку документа
###############

###########################ADMINS

admins = [6575606312,916438269,748788690]  #here u need to paste user id of SUPERADMINS first is mine i will delte second is yours by ,


@dp.callback_query_handler(lambda message: message.data == 'cleanCart')
async def sellerProfile(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.answer("Cart is clear!",show_alert=True)
    cursor.execute("DELETE FROM cart WHERE user_id = ?",(call.from_user.id,))
    conn.commit()
    cursor.execute("SELECT id FROM sellers where user_id = ?", (call.from_user.id,))
    userExists = cursor.fetchone()
    await call.message.edit_text(dict_message["mainMenu"],
                                 reply_markup=await keyboard.mainMenu(True if userExists else False))


@dp.callback_query_handler(lambda message: message.data == 'sellerProfile')
async def sellerProfile(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    cursor.execute("SELECT balance FROM sellers WHERE user_id = ?", (call.from_user.id,))
    balance = cursor.fetchone()
    cursor.execute("SELECT * FROM bases WHERE seller_id = ?", (call.from_user.id,))
    products = cursor.fetchall()
    cursor.execute("SELECT SUM(price) FROM sales WHERE seller_id = ?",(call.from_user.id,))
    soldAllPrice = cursor.fetchone()
    cursor.execute("SELECT COUNT(id) FROM sales WHERE seller_id = ? and dates = CURRENT_DATE ",(call.from_user.id,))
    soldToday = cursor.fetchone()
    cursor.execute("SELECT COUNT(id) FROM sales WHERE seller_id = ?",(call.from_user.id,))
    soldTotal = cursor.fetchone()
    countFullz = 0
    cursor.execute("SELECT SUM(price) FROM refund WHERE user_id = ? and status = ?",
                   (call.from_user.id,"accepted",))
    refund = cursor.fetchone()

    for product in products:
        countFile = scriptForFile.countCC(f"src/{product[2]}")
        countFullz +=countFile
    await call.message.edit_text("Your profile!\n"
                                 f"Seller balance: <b>£{round(balance[0],1)}</b>\n"
                                 f"Your products: <b>{countFullz}</b>\n"
                                 f"Sold today: <b>{soldToday[0]}</b>\n"
                                 f"Sold total: <b>{soldTotal[0]}</b>\n"
                                 f"Refunds: £<b>{round(refund[0],1) if refund[0] else 0}</b>\n"
                                 f"Sold: £<b>{soldAllPrice[0] if soldAllPrice[0] else 0}</b>", parse_mode="HTML", reply_markup=await keyboard.sellerPage())



class SellerWithdraw(StatesGroup):
    address = State()



#####

class Deposit(StatesGroup):
    summa = State()


#####DepositCustomer
@dp.callback_query_handler(lambda message: message.data == 'customerWallet')
async def customerWallet(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()

    cursor.execute("SELECT * FROM deposits WHERE user_id = ? and status = ?", (call.from_user.id, 0,))
    payData = cursor.fetchone()
    if payData:
        paymentID = payData[2]
        status, address, pay_amount, crypto,price_amount = payment.checkPayment(paymentID)
        await call.message.edit_text(
            text=dict_message["guest_payment_usd"].format(paymentID, round(pay_amount, 5), address) if crypto == "usdt"
            else dict_message["guest_payment"].format(paymentID, round(pay_amount, 5), crypto.upper(), address),
            parse_mode="HTML",
            reply_markup=await keyboard.checkDeposit(paymentID))
    else:
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (call.from_user.id,))
        balance = cursor.fetchone()
        await call.message.edit_text(f"Customer balance: <b>£{balance[0]}</b>\nChoose what crypto to deposit",
                                 parse_mode="HTML",
                                 reply_markup=await keyboard.chooseDepositCrypto())


@dp.callback_query_handler(text_contains="newDeposit")
async def depositCryptoType(call: types.CallbackQuery, state=FSMContext):
    await state.reset_state()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (call.from_user.id,))
    balance = cursor.fetchone()
    await call.message.edit_text(f"Customer balance: <b>£{balance[0]}</b>\nChoose what crypto to deposit",
                                 parse_mode="HTML",
                                 reply_markup=await keyboard.chooseDepositCrypto())
    cursor.execute("DELETE FROM deposits WHERE user_id = ? and status = ?",(call.from_user.id,0,))
    conn.commit()

@dp.callback_query_handler(text_contains="topup")
async def depositCryptoType(call: types.CallbackQuery, state=FSMContext):
    cryptoType = call.data.split(":")[1]
    await call.message.edit_text("Amount you want to deposit", reply_markup=None)
    await state.update_data(crypto=cryptoType, cid=call.message.message_id)
    await Deposit.summa.set()


@dp.message_handler(content_types=["text"], state=Deposit.summa)
async def depositShowAddress(message: types.Message, state=FSMContext):
    data = await state.get_data()
    await state.finish()
    address, payment_id, pay_amount = payment.createTopUp(message.text, data["crypto"], message.from_user.id)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=data['cid'],
                                text=f'Please send money to the address below: '
                                     f'\n\n<code>{address}</code>\n\nAmount:\n\n<code>{pay_amount}</code>\n\n'
                                     f'This address can only be used once.',
                                parse_mode='HTML', reply_markup=await keyboard.iPaidDeposit(payment_id))
    await message.delete()

@dp.callback_query_handler(text_contains = 'payDeposit')
async def paymentPage(call: types.CallbackQuery):
    paymentID = call.data.split(":")[1]
    cursor.execute("INSERT INTO deposits (user_id,paymentID,status) VALUES (?,?,?)", (call.from_user.id,
                                                                                      paymentID,
                                                                                      0))
    conn.commit()
    await call.message.edit_reply_markup(await keyboard.checkDeposit(paymentID))


@dp.callback_query_handler(text_contains="checkTopUp", state='*')
async def paidSeller(call: types.CallbackQuery, state=FSMContext):
    paymentID = call.data.split(":")[1]
    depositStatus,address,price,crypto,price_amount = payment.checkPayment(paymentID)
    if depositStatus == "waiting":
        await call.answer("Funds have not yet been received", show_alert=True)
    elif depositStatus == "confirming":
        await call.answer("Funds is confirming!", show_alert=True)
    elif depositStatus in ["confirmed", 'sending', 'finished']:

        cursor.execute("UPDATE users SET balance =balance + ? WHERE user_id = ?", (price_amount, call.from_user.id,))
        cursor.execute("UPDATE deposits SET status = 1 WHERE paymentID = ?", (paymentID,))
        conn.commit()
        await call.answer("Fund is deposited!", show_alert=True)
        cursor.execute("SELECT id FROM sellers where user_id = ?", (call.from_user.id,))
        userExists = cursor.fetchone()
        await call.message.edit_text(dict_message["mainMenu"],
                                     reply_markup=await keyboard.mainMenu(True if userExists else False))

    elif depositStatus == 'failed':
        await call.answer("Something went wrong, text to admins".upper(), show_alert=True)


@dp.callback_query_handler(lambda message: message.data == 'decreaseProduct')
async def sellerDeleteProduct(call: types.CallbackQuery):
    cursor.execute("SELECT baseID,pathFile FROM bases WHERE seller_id = ?", (call.from_user.id,))
    bases = cursor.fetchall()
    productList = []
    for base in bases:
        cursor.execute("SELECT * FROM products WHERE id = ?", (base[0],))
        productList.append({base[0]:[cursor.fetchone(),base[1]]})
    await call.message.edit_text("Choose product to delete\n\nCategory | Country | Base | Count ", reply_markup=await keyboard.showDeleteProduct(productList,))


@dp.callback_query_handler(text_contains="deleteBase", state='*')
async def paidSeller(call: types.CallbackQuery, state=FSMContext):
    pathFile = call.data.split(":")[1]
    cursor.execute("DELETE FROM bases WHERE pathFile  =  ?", (pathFile,))
    conn.commit()
    await call.message.edit_text("File deleted!", reply_markup=await keyboard.cancelSeller())


@dp.callback_query_handler(lambda message: message.data == 'withdrawSeller')
async def sellerProfileWithdraw(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("SELECT balance FROM sellers WHERE user_id = ?", (call.from_user.id,))
    balance = cursor.fetchone()
    if balance[0] < 30:
        await call.message.edit_text("Your balance should be more than £30", reply_markup=await keyboard.cancelSeller())
    else:
        await call.message.edit_text("Send your BTC address", reply_markup=await keyboard.cancelSeller())
        await SellerWithdraw.address.set()


@dp.message_handler(state=SellerWithdraw.address)
async def sellerWithdraw(message: types.Message, state=FSMContext):
    cursor.execute("SELECT balance FROM sellers WHERE user_id = ?", (message.from_user.id,))
    balance = cursor.fetchone()
    cursor.execute("INSERT INTO withdrawed(user_id,summa,address,paid) VALUES (?,?,?,?)",
                   (message.from_user.id, balance[0], message.text, 0))
    cursor.execute("UPDATE sellers SET balance = 0 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    cursor.execute("SELECT id FROM withdrawed ORDER BY id DESC LIMIT 1")
    lastID = cursor.fetchone()
    for admin in admins:
        await bot.send_message(chat_id=admin,
                               text=f"Send £<b>{balance[0]}</b> to \n"
                                    f"<code>{message.text}</code>", parse_mode="HTML",
                               reply_markup=await keyboard.withdrawedMoneyToSeller(lastID[0]))
    await state.reset_state()
    await message.answer("You will be paid soon!", reply_markup=await keyboard.cancelSeller())


@dp.callback_query_handler(text_contains="paySeller", state='*')
async def paidSeller(call: types.CallbackQuery):
    recordID = call.data.split(":")[1]
    cursor.execute("SELECT * FROM withdrawed WHERE id = ?", (recordID,))
    user = cursor.fetchone()
    cursor.execute("UPDATE withdrawed SET paid = 1 WHERE id = ?", (recordID,))
    conn.commit()
    await bot.send_message(chat_id=user[1], text="The money has been transferred, please wait",
                           reply_markup=await keyboard.cancelSeller())


#######SUPERADMIN

@dp.message_handler(commands=["superadmin"], state='*')
async def superadmin(message: types.Message):
    if message.from_user.id in admins:
        cursor.execute("SELECT active FROM status WHERE name = ?",("guestPayment",))
        active = cursor.fetchone()
        await message.answer("Super admin", reply_markup=await keyboard.superAdmin(active[0]))


@dp.callback_query_handler(lambda message: message.data == "superadmin", state='*')
async def superadmin(call: types.CallbackQuery,state:FSMContext):
    await state.reset_state()
    cursor.execute("SELECT active FROM status WHERE name = ?", ("guestPayment",))
    active = cursor.fetchone()
    await call.message.edit_text("Super admin", reply_markup=await keyboard.superAdmin(active[0]))


class Category(StatesGroup):
    category = State()


@dp.callback_query_handler(lambda message: message.data == 'changeBuyAccess')
async def superAdminAddCategory(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("SELECT active FROM status WHERE name = ?", ("guestPayment",))
    active = cursor.fetchone()
    if active[0] == 1:
        cursor.execute("UPDATE status SET active = ? WHERE name = ?",(0,"guestPayment"))
    elif active[0] == 0:
        cursor.execute("UPDATE status SET active = ? WHERE name = ?",(1,"guestPayment"))
    conn.commit()
    cursor.execute("SELECT active FROM status WHERE name = ?", ("guestPayment",))
    active = cursor.fetchone()
    await call.message.edit_text("Super admin", reply_markup=await keyboard.superAdmin(active[0]))

@dp.callback_query_handler(lambda message: message.data == 'addCategory')
async def superAdminAddCategory(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Write a new cateogry", reply_markup=await keyboard.cancelSuperAdmin())
    await state.update_data(mid=call.message.message_id)
    await Category.category.set()


@dp.message_handler(state=Category.category)
async def superAdminInsertingCategory(message: types.Message, state=FSMContext):
    data = await state.get_data()
    cursor.execute("INSERT INTO category (category) VALUES (?)", (message.text,))
    conn.commit()
    await message.delete()
    cursor.execute("SELECT active FROM status WHERE name=?", ("guestPayment",))
    guestPayment = cursor.fetchone()
    await bot.edit_message_text(chat_id=message.chat.id, message_id=data["mid"],
                                text="New category added", reply_markup=await keyboard.superAdmin(guestPayment[0]))
    await state.finish()


@dp.callback_query_handler(lambda message: message.data == 'delCategory')
async def superAdminDelCategory(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()
    await call.message.edit_text("Choose category to delete", reply_markup=await keyboard.deleteCategory(categories))


@dp.callback_query_handler(text_contains='deletingCategory')
async def superAdminDelCategory(call: types.CallbackQuery, state: FSMContext):
    categoryID = call.data.split(":")[1]
    cursor.execute("DELETE FROM category WHERE id = ?", (categoryID,))
    conn.commit()
    await call.message.edit_text("Category deleted", reply_markup=await keyboard.cancelSuperAdmin())
###########Downloading file

@dp.callback_query_handler(text_contains='downloadSuperAdmin')
async def superAdminDelCategory(call: types.CallbackQuery, state: FSMContext):
    orderID = call.data.split(":")[1]
    cursor.execute("SELECT pathFile FROM sales WHERE id = ?", (orderID,))
    pathFile = cursor.fetchone()[0]
    await bot.send_document(chat_id=call.from_user.id,document=InputFile(f"{pathFile}"))



@dp.callback_query_handler(text_contains='decisionRefund')
async def superAdminDelCategory(call: types.CallbackQuery, state: FSMContext):
    orderID = call.data.split(":")[1]
    decision = call.data.split(":")[2]
    cursor.execute("SELECT * FROM sales WHERE id = ?",(orderID,))
    saleInfo = cursor.fetchone()
    cursor.execute("SELECT status FROM refund WHERE  orderID = ?",(orderID,))
    order = cursor.fetchone()
    if order[0]:
        await call.message.edit_text("The decision has already been made by other superadmin",reply_markup=await keyboard.mainMenu(False))
    else:
        if decision == "accepted":
            price = saleInfo[3]
            await bot.send_message(chat_id=saleInfo[2],
                                   text="Your refund was accepted\nRefreshed your wallet!")
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?",
                           (price,saleInfo[2]))

            cursor.execute("SELECT percentage FROM userPercentage WHERE user_id=?", (saleInfo[4],))
            percentage = cursor.fetchone()
            sellerSold = float(scriptForFile.percentage(price, percentage[0]))
            cursor.execute("UPDATE sellers SET balance = balance - ? WHERE user_id = ?",(round(sellerSold,1),saleInfo[4],))
            conn.commit()
            cursor.execute("Update sellers SET balance = balance - ? WHERE user_id = ?",
                               (round(price-sellerSold,1), 777,))
            conn.commit()
            cursor.execute("UPDATE refund SET status = ? WHERE orderID = ?",("accepted",orderID))
            conn.commit()
            await bot.send_message(chat_id=saleInfo[4],text="Refund was done!\nBelow you can download file",reply_markup=await keyboard.downloadFile(orderID))
            await call.message.edit_text("Accepted",reply_markup=await keyboard.cancelSuperAdmin())
        else:
            await bot.send_message(chat_id=saleInfo[2],
                                   text="Your refund was rejected")
            cursor.execute("UPDATE refund SET status = ? WHERE orderID = ?", ("rejected", orderID))
            conn.commit()
            await call.message.edit_text("Rejected",reply_markup=await keyboard.cancelSuperAdmin())


@dp.callback_query_handler(lambda message: message.data == 'listOfRefunds')
async def insertProduct(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("SELECT * FROM refund WHERE status is NULL")
    refunds = cursor.fetchall()
    await call.message.edit_text("Active refund list",reply_markup=await keyboard.showRefunds(refunds))


@dp.callback_query_handler(text_contains='showExactRefund')
async def insertProductCategory(call: types.CallbackQuery, state: FSMContext):
    orderID = call.data.split(":")[1]
    await call.message.edit_text(f"Order id: {orderID}",reply_markup=await keyboard.adminRefundSystem(orderID))
class Base(StatesGroup):
    category = State()
    country = State()
    name = State()
    price = State()
    file = State()



@dp.callback_query_handler(lambda message: message.data == 'withdrawRequests')
async def withdrawRequest(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("SELECT * FROM withdrawed where paid = 0")
    withdrawRequests = cursor.fetchall()
    await call.message.edit_text("Withdraw requests",reply_markup=await keyboard.showRequests(withdrawRequests))



######INSERTING PRODUCT SYSTEM
@dp.callback_query_handler(text_contains='showExactRequest')
async def insertProductCategory(call: types.CallbackQuery, state: FSMContext):
    requestID = call.data.split(":")[1]
    cursor.execute("SELECT * FROM withdrawed WHERE id = ?",(requestID,))
    withdrawInfo = cursor.fetchone()
    userInfo =await bot.get_chat_member(withdrawInfo[1],withdrawInfo[1])
    user = userInfo.user
    await call.message.edit_text("Username | Withdrawed | Address\n\n"
                                      f"{user['username'] if user['username'] else 'No username'} | {withdrawInfo[2]} | {withdrawInfo[3]}",
                                 reply_markup=await keyboard.withdrawedMoneyToSeller(requestID))




@dp.callback_query_handler(lambda message: message.data == 'delBase')
async def insertProduct(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("SELECT category FROM products GROUP BY category")
    categories = cursor.fetchall()
    await call.message.edit_text("Choose a category", reply_markup=await keyboard.delBaseCategory(categories))


@dp.callback_query_handler(text_contains='delBaseCategory')
async def insertProductCategory(call: types.CallbackQuery, state: FSMContext):
    category = call.data.split(":")[1]
    cursor.execute("SELECT country FROM products WHERE category = ? GROUP BY country",(category,))
    countries = cursor.fetchall()

    await call.message.edit_text("Choose country", reply_markup=await keyboard.delBaseCountry(category,countries))


@dp.callback_query_handler(text_contains='delBaseCountry')
async def insertProductCategory(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    country  = call.data.split(":")[2]
    cursor.execute("SELECT * FROM products WHERE category = ? and country =?",(category,country))
    products = cursor.fetchall()
    await call.message.edit_text("Choose country", reply_markup=await keyboard.delBaseProduct(products))




@dp.callback_query_handler(text_contains='delBaseProduct')
async def insertProductCategory(call: types.CallbackQuery):
    productID = call.data.split(":")[1]
    cursor.execute("DELETE FROM products WHERE id = ?",(productID))
    conn.commit()
    await call.message.edit_text("Deleted!", reply_markup=await keyboard.cancelSuperAdmin())




@dp.callback_query_handler(lambda message: message.data == 'addBase')
async def insertProduct(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()
    await call.message.edit_text("Choose a category", reply_markup=await keyboard.insertChooseCategory(categories))
    await Base.category.set()


######INSERTING PRODUCT SYSTEM
@dp.callback_query_handler(text_contains='category', state=Base.category)
async def insertProductCategory(call: types.CallbackQuery, state: FSMContext):
    category = call.data.split(":")[1]
    await state.update_data(category=category, mid=call.message.message_id)
    await call.message.edit_text("Write name of country", reply_markup=None)
    await Base.country.set()


@dp.message_handler(state=Base.country)
async def insertProductCountry(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("SELECT category FROM category WHERE id = ?", (data['category'],))
    category = cursor.fetchone()
    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=data["mid"],
                                text=f"Category: <b>{category[0]}</b>\n"
                                     f"Country: <b>{message.text}</b>\n"
                                     f"Please write name of Base",
                                parse_mode="HTML")
    await state.update_data(country=message.text, categoryName=category[0])
    await message.delete()
    await Base.name.set()


@dp.message_handler(state=Base.name)
async def insertProductName(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=data["mid"],
                                text=f"Category: <b>{data['categoryName']}</b>\n"
                                     f"Country: <b>{data['country']}</b>\n"
                                     f"Name: <b>{message.text}</b>\n"
                                     f"Please write price of item",
                                parse_mode="HTML")
    await state.update_data(name=message.text)
    await message.delete()
    await Base.price.set()


@dp.message_handler(state=Base.price)
async def insertProductPrice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=data["mid"],
                                text=f"Category: <b>{data['categoryName']}</b>\n"
                                     f"Country: <b>{data['country']}</b>\n"
                                     f"Name: <b>{data['name']}</b>\n"
                                     f"Price: <b>{message.text}</b>\n"
                                     f"Base added succesfully",
                                parse_mode="HTML",reply_markup=await keyboard.cancelSuperAdmin())
    cursor.execute("INSERT INTO products(category,country,name,price) VALUES (?,?,?,?)",
                                      (data['categoryName'], data["country"].upper(), data["name"], message.text,))
    conn.commit()
    await message.delete()
    await state.finish()


@dp.callback_query_handler(lambda message: message.data == 'resetBalance')
async def resetBalance(call: types.CallbackQuery, state: FSMContext):
    cursor.execute("UPDATE sellers SET balance = 0.0 WHERE user_id = 777")
    conn.commit()
    await call.message.edit_text("Reset was done!",reply_markup=await keyboard.backToStats())

@dp.callback_query_handler(lambda message: message.data == 'statistics')
async def sellerProfile(call: types.CallbackQuery, state: FSMContext):

    cursor.execute("SELECT sum(price) FROM sales")
    soldTotal = cursor.fetchone()
    cursor.execute("SELECT user_id FROM sellers")
    sellers = cursor.fetchall()
    cursor.execute("SELECT balance  FROM sellers WHERE user_id = 777")
    sellerBalance = cursor.fetchone()
    mainText = (f"Admin balance: £{round(sellerBalance[0],1) if sellerBalance[0] else 0}\n"
                f"Sold total: £{soldTotal[0] if soldTotal[0] else 0}\n"
                f"Sold total: £{soldTotal[0] if soldTotal[0] else 0}\n\n")
    await call.message.edit_text(mainText,parse_mode="HTML",reply_markup=await keyboard.showSellers(sellers))



@dp.callback_query_handler(text_contains='showSeller')
async def insertProductCategory(call: types.CallbackQuery):
    sellerId = call.data.split(":")[1]
    cursor.execute("SELECT SUM(price) FROM sales WHERE seller_id = ? and dates = CURRENT_DATE",(sellerId,))
    soldToday = cursor.fetchone()
    cursor.execute("SELECT SUM(price) FROM sales WHERE seller_id = ?",(sellerId,))
    soldTotal = cursor.fetchone()
    userInfo = await bot.get_chat_member(int(sellerId),int(sellerId))
    username = userInfo.user["username"]
    cursor.execute("SELECT balance from sellers where user_id = ?",(sellerId,))
    balance = cursor.fetchone()
    cursor.execute("SELECT * FROM bases WHERE seller_id = ?",(sellerId,))
    products = cursor.fetchall()
    countFullz = 0
    cursor.execute("SELECT SUM(price) FROM refund WHERE user_id = ? and status = ?",
                   (sellerId, "accepted",))
    refund = cursor.fetchone()
    for product in products:
        countFile = scriptForFile.countCC(f"src/{product[2]}")
        countFullz +=countFile
    cursor.execute("SELECT COUNT(id) FROM sales WHERE seller_id = ?",(sellerId,))
    countQuantity = cursor.fetchone()
    cursor.execute("SELECT percentage FROM userPercentage WHERE user_id = ?",(sellerId,))
    percentage = cursor.fetchone()
    await call.message.edit_text(f"Username: @{username}\n"
                                f"Seller percentage: <b>{percentage[0]}%</b>\n"
                                f"Seller balance: <b>£{round(balance[0],1)}</b>\n"
                                f"Seller products: <b>{countFullz}</b>\n"
                                f"Sold products: <b>{countQuantity[0]}pcs</b>\n"
                                f"Sold today: £{soldToday[0] if soldToday[0] else 0}\n"
                                f"Sold total: £{soldTotal[0] if soldTotal[0] else 0}\n"
                                f"Refunds: £<b>{round(refund[0],1) if refund[0] else 0}</b>\n",parse_mode="HTML"
                                 ,reply_markup=await keyboard.deleteSeller(sellerId))

class Percentage(StatesGroup):
    percentage = State()


@dp.callback_query_handler(text_contains='changePercentage')
async def insertProductCategory(call: types.CallbackQuery,state:FSMContext):
    sellerID = call.data.split(":")[1]
    await call.message.edit_text("Write new percentage of product")
    await state.update_data(sellerID = sellerID, mid=call.message.message_id)
    await Percentage.percentage.set()

@dp.message_handler(state=Percentage.percentage)
async def editinPricePrice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("UPDATE userPercentage SET percentage = ? WHERE user_id =?",
                   (int(message.text), data["sellerID"],))
    conn.commit()
    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=data["mid"],
                                text="Percentage edited",reply_markup=await keyboard.cancelSuperAdmin()
                                )
    await message.delete()
    await state.finish()


@dp.callback_query_handler(text_contains='deleteSeller')
async def insertProductCategory(call: types.CallbackQuery):
    sellerId = call.data.split(":")[1]
    cursor.execute("DELETE FROM sellers WHERE user_id = ?",(sellerId,))
    cursor.execute("DELETE FROM bases WHERE seller_id = ?",(sellerId,))
    conn.commit()
    await call.message.edit_text("Seller was delete",reply_markup=await keyboard.cancelSuperAdmin())



##########EDITING PRICE
class Price(StatesGroup):
    price = State()

@dp.callback_query_handler(lambda message: message.data == 'editPrice')
async def editinPrice(call: types.CallbackQuery):
    cursor.execute("SELECT category FROM products GROUP BY category")
    categories = cursor.fetchall()
    await call.message.edit_text("Choose category of product to edit",reply_markup= await keyboard.editPrice(categories))

@dp.callback_query_handler(text_contains='categoryEditPric')
async def insertProductCategory(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    cursor.execute("SELECT country FROM products WHERE category = ? GROUP BY country",(category,))
    countries = cursor.fetchall()
    await call.message.edit_text("Choose country", reply_markup=await keyboard.editPriceCountry(category,countries))

@dp.callback_query_handler(text_contains='countryEditPric')
async def insertProductCategory(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    country  = call.data.split(":")[2]
    cursor.execute("SELECT * FROM products WHERE category = ? and country = ?",(category,country,))
    products = cursor.fetchall()
    await call.message.edit_text("Choose file to edit price",
                                 reply_markup=await keyboard.productEditPrice(category,products))

@dp.callback_query_handler(text_contains='editPriceProduct')
async def insertProductCategory(call: types.CallbackQuery,state:FSMContext):
    productID = call.data.split(":")[1]
    await call.message.edit_text("Write new price of product")
    await state.update_data(productID = productID, mid = call.message.message_id)
    await Price.price.set()

@dp.message_handler(state=Price.price)
async def editinPricePrice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("UPDATE products SET price = ? WHERE id =?",(int(message.text),data["productID"],))
    conn.commit()
    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=data["mid"],
                                text="Price edited",
                                )
    await message.delete()
    await state.finish()



class Name(StatesGroup):
    name = State()

@dp.callback_query_handler(lambda message: message.data == 'editName')
async def editinPrice(call: types.CallbackQuery):
    cursor.execute("SELECT category FROM products GROUP BY category")
    categories = cursor.fetchall()
    await call.message.edit_text("Choose category of product to edit name",reply_markup= await keyboard.nameEdit(categories))

@dp.callback_query_handler(text_contains='categoryEditName')
async def insertProductCategory(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    cursor.execute("SELECT country FROM products WHERE category = ? GROUP BY country",(category,))
    countries = cursor.fetchall()
    await call.message.edit_text("Choose country", reply_markup=await keyboard.editNameCountry(category,countries))


@dp.callback_query_handler(text_contains='countryEditName')
async def insertProductCategory(call: types.CallbackQuery):
    category = call.data.split(":")[1]
    country  = call.data.split(":")[2]
    cursor.execute("SELECT * FROM products WHERE category = ? and country = ?",(category,country,))
    products = cursor.fetchall()
    await call.message.edit_text("Choose base to edit name",
                                 reply_markup=await keyboard.nameEditName(category,products))


@dp.callback_query_handler(text_contains='nameEditName')
async def insertProductCategory(call: types.CallbackQuery,state:FSMContext):
    productID = call.data.split(":")[1]
    await call.message.edit_text("Write new name of product")
    await state.update_data(productID = productID, mid = call.message.message_id)
    await Name.name.set()


@dp.message_handler(state=Name.name)
async def editinPricePrice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute("UPDATE products SET name = ? WHERE id =?",(message.text,data["productID"],))
    conn.commit()
    await bot.edit_message_text(chat_id=message.from_user.id,
                                message_id=data["mid"],
                                text="Name edited",
                                reply_markup=await keyboard.cancelSuperAdmin())
    await message.delete()
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
