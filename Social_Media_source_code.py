import discord , random ,time , asyncio ,sqlite3,datetime , json  , re
from discord.ext import commands 
from discord import Embed , app_commands
from discord.ui import Button , View , Modal    
# from discord.ext.commands import has_permissions
from discord.ext.commands import MissingPermissions, CommandNotFound,MemberNotFound
#validators
# -----------------------------{Data 1}-----------------------------
db = sqlite3.connect("data.db")
cr = db.cursor()
# -----------------------------{Data 2}-----------------------------

async def is_main_guild(ctx):
    if ctx.guild.id == main_guild :
        return True
    else:
        embedd = discord.Embed(colour=0x0070FF ,title=f"Create your account in main server", url = "https://discord.gg/e2KuwGNEVa", description=  f"")
        embedd.add_field(name="Main server :" ,value=f"https://discord.gg/e2KuwGNEVa \n{ctx.user.mention} :``go in main server and create your account``", inline= False)
        embedd.set_thumbnail(url= ctx.user.display_avatar.url)
        await ctx.user.send(f"{ctx.user.mention}" , embed = embedd  , view = Seen())        
        return False


def is_have_account(user_id): 
    cr.execute(f"select user_id from registers_users where user_id = '{user_id}'")
    check = cr.fetchone()
    if check != None :
        have_account = True
        cr.execute(f"select user_status from registers_users where user_id = '{user_id}'")
        user_status = cr.fetchone()[0]
        if user_status == "True" :
            logined = True

        else:
            logined = False

    else:
        have_account = False
        logined = False

    data = {
        "have_account" : have_account ,
        "logined" : logined
    }


    return data


async def is_have_account2(ctx ):
    user_id = ctx.user.id
    # cr.execute(f"select user_id from registers_users where user_id = '{user_id}'")
    # check = cr.fetchone()

    check = is_have_account(user_id)["logined"]
    if check == True :
        have_account = True
    else:
        have_account = False
        embedd = discord.Embed(colour=0x0070FF ,title=f"You don't have account yet or you didn't login yet", url = "https://discord.gg/e2KuwGNEVa", description=  f"")
        embedd.add_field(name="Main server :" ,value=f"https://discord.gg/e2KuwGNEVa \n{ctx.user.mention} :``go in main server and create your account or login``", inline= False)
        embedd.set_thumbnail(url= ctx.user.display_avatar.url)
        await ctx.user.send(f"{ctx.user.mention}" , embed = embedd  , view = Seen())

    return have_account




def not_have_account( data):
    if data['have_account'] == True and data['logined'] == False :
        embedd = discord.Embed(colour=0x0070FF ,title=f"you are not login" , description=  f"")
        embedd.add_field(name="Status :red_circle::" , value=f"please go in main server and do``{perfix}login``" , inline=False)
        embedd.set_footer(text=footer())
        return embedd
    elif data['have_account'] == False :
        embedd = discord.Embed(colour=0x0070FF ,title=f"you don't have account  yet" , description=  f"")
        embedd.add_field(name="Status :red_circle::" , value=f"please go in main server and do``{perfix}register``" , inline=False)
        embedd.set_footer(text=footer())
        return embedd

def is_username_avaible(username):
    if len(username) < 3:
        return "invaild"
    if(bool(re.search('^[a-z0-9_]*$',username))==True):
        cr.execute(f"select username from registers_users where username = '{username}'")
        check = cr.fetchone()
        if check == None :
            return True
        else:
            return False

    else:
        return "invaild"




async def check_account_room(interaction):
    room = interaction.channel.id 
    if room  == account_room:
        return True
    else:
        await interaction.response.send_message("**Go In account room**",ephemeral= True )
        return False

    
def ar_bluoz(user_id , num , fun):
    if fun == "A":
        cr.execute(f"update registers_users set bluoz = (bluoz + {num} ) where user_id = '{user_id}'")
    elif fun == "R":
        cr.execute(f"update registers_users set bluoz = (bluoz - {num} ) where user_id = '{user_id}'")
    db.commit()


def footer():
    embed_footer = f"©2022 BlueLion | Social Media Bot All Right Reserved."
    return embed_footer





class Seen(View):
    def __init__(self):
        
        super().__init__(timeout=None)



    @discord.ui.button(label= "", style=discord.ButtonStyle.gray, custom_id="seen" , emoji="👁")
    async def seen_button(self , interaction:discord.interactions , button:discord.Button):
        await interaction.message.delete()


# -----------------------------{Finaly}-----------------------------


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=perfix, intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(Post_view())
        self.add_view(Seen())
        self.add_view(report_view())
        self.add_view(Lang())
        self.add_view(Ntf())
        await check()
        await check_watch_before(all= True)


client = MyBot()
tree = client.tree

# -----------------------------{Register-Login -=> System}-----------------------------

@client.tree.command(name="register",description="register command")
@app_commands.guild_only()
@app_commands.check(is_main_guild)
@app_commands.check(check_account_room)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
async def register(interaction:discord.interactions,username:str):
    user_id =interaction.user.id 
    data = is_have_account(user_id)

    if data['have_account'] == False:
        check = is_username_avaible(username=username)
        if check == True:
            cr.execute(f"insert into registers_users(user_id , user_status , username) values (?,?,?)" , (user_id,'False' ,username.capitalize() , ))
            db.commit()
            embedd = discord.Embed(colour=0x0070FF ,title="Successfully registered   :robot:" , description=  f"You have reigster as ``{username.capitalize()}``")
            embedd.set_footer(text=footer())        
            # await ctx.message.delete(delay = 3)
            await interaction.response.send_message(embed = embedd ,ephemeral= False )
        elif check == False:
            embedd = discord.Embed(colour=0x0070FF ,title=f"Username unavaible 😥" , description=  f"Please try register with another username")
            embedd.set_footer(text=footer())        
            # await ctx.message.delete(delay = 3)            
            await interaction.response.send_message(embed = embedd ,ephemeral= True )


        elif check == "invaild":
            embedd = discord.Embed(colour=0x0070FF ,title=f"Invaild username ❌" , description=  f"Please try register with another username ``(a-z 0-9 _) And at least 3 letter``")
            # await ctx.message.delete(delay = 3)
            await interaction.response.send_message(embed = embedd ,ephemeral= True )



    elif data['have_account'] == True :
        embedd = discord.Embed(colour=0x0070FF ,title=f"You have account already   :identification_card:" , description=  f"Please login to be able to use our features \n-=>``{perfix}login``")
        embedd.set_footer(text=footer())
        # await ctx.message.delete(delay = 3)
        await interaction.response.send_message(embed = embedd ,ephemeral= True )



@client.tree.command(name="login",description="login command")
@app_commands.guild_only()
@app_commands.check(is_main_guild)
@app_commands.check(check_account_room)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
async def login(interaction:discord.interactions):
    user_id = interaction.user.id
    data = is_have_account(user_id)

    if data['have_account'] == True:
        username = await get_username_from_id(user_id)
        rank = await get_rule_from_id(user_id)
        check2 = await get_lang_from_id(interaction.user.id)
        if check2 == "ar" or check2 == "en":

            if data['logined'] == True:
                
                embedd = discord.Embed(colour=0x0070FF ,title=f"You are login already   :identification_card:" , description=  f"You are login as ``{username}``")
                embedd.set_footer(text=footer())
                await interaction.response.send_message(embed = embedd ,ephemeral= True )

            else:

                embedd = discord.Embed(colour=0x0070FF ,title="Successfully login   :robot:" , description=  f"You have login as ``{username}``")
                embedd.set_footer(text=footer())
                await interaction.response.send_message(embed = embedd ,ephemeral= True )
                cr.execute(f"update registers_users set user_status = 'True' where user_id = '{user_id}'")
                db.commit()
                role = (interaction.guild).get_role(activate_role)
                await (interaction.user).add_roles(role)
                await(interaction.user).edit(nick = f"[{rank}] {username}")
                if check2 == "ar":
                    arabic_rolee = (interaction.guild).get_role(arabic_role)
                    await (interaction.user).add_roles(arabic_rolee)
                elif check2 == "en":
                    english_rolee = (interaction.guild).get_role(english_role)
                    await (interaction.user).add_roles(english_rolee)                              

        else:
            embedd = discord.Embed(colour=0x0070FF ,title="You must select your lang" , description=  f"**go Intro channel**")
            embedd.set_footer(text=footer())
            await interaction.response.send_message(embed = embedd ,ephemeral= True )


    else:
        embedd = not_have_account(data)
        await interaction.response.send_message(embed = embedd ,ephemeral= True )



async def check():
    guild = await client.fetch_guild(main_guild)
    cr.execute("select user_id from registers_users where user_status = 'True' ")
    users_registerd_before = cr.fetchall()
    for member in users_registerd_before : 
        user_id = int(member[0])
        try:
            ttp = await guild.fetch_member(user_id)
        except:
            cr.execute(f"update registers_users set user_status = 'False' where user_id = '{user_id}'")
            db.commit()


async def check2(member):
    # -------------------{part of -=> Register-Login -=> System}-----------------
    user_id = member.id
    try:
        cr.execute(f"update registers_users set user_status = 'False' where user_id = '{user_id}'")
        db.commit()
    except:
        pass

# -----------------------------{-Intro -=> System}-----------------------------




class Lang(View):
    def __init__ (self ) :
        
        super().__init__(timeout=None)   




    @discord.ui.button(label="Arabic" , style=discord.ButtonStyle.gray, custom_id="Arabic" , emoji="🍔" , row= 0)
    async def arabic_button (self , interaction:discord.interactions , button:discord.Button):
        check = is_have_account(interaction.user.id)
        if check["have_account"] == True:
            await interaction.response.send_message("**you have been selected Arabic lang🟢**",ephemeral = True)
            await set_lang_from_id(interaction.user.id , "ar")

            english_rolee = (interaction.guild).get_role(english_role)
            await (interaction.user).remove_roles(english_rolee)          

            arabic_rolee = (interaction.guild).get_role(arabic_role)
            await (interaction.user).add_roles(arabic_rolee)
        else:
            await interaction.response.send_message("**You don't Have Account Yet**" , ephemeral = True)



    @discord.ui.button(label="English" , style=discord.ButtonStyle.gray, custom_id="English" , emoji="🍕" , row= 0)
    async def english_button (self , interaction:discord.interactions , button:discord.Button):
        check = is_have_account(interaction.user.id)
        if check["have_account"] == True:
            await interaction.response.send_message("**you have been selected English lang🟢**",ephemeral = True)
            await set_lang_from_id(interaction.user.id , "en")    

            arabic_rolee = (interaction.guild).get_role(arabic_role)
            await (interaction.user).remove_roles(arabic_rolee)

            english_rolee = (interaction.guild).get_role(english_role)
            await (interaction.user).add_roles(english_rolee)          

        else:
            await interaction.response.send_message("**You don't Have Account Yet**" , ephemeral = True)




class Ntf(View):
    def __init__ (self ) :
        
        super().__init__(timeout=None)   


    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="on_ntf" , emoji="🟢" , row= 0)
    async def on_ntf_button (self , interaction:discord.interactions , button:discord.Button):
        check = is_have_account(interaction.user.id)
        if check["have_account"] == True:        
            user_id = interaction.user.id
            await of_ntf(user_id= user_id , fun= "on")
            await interaction.response.send_message("**you have been turn on your notification🟢**",ephemeral = True)
        else:
            await interaction.response.send_message("**You don't Have Account Yet**" , ephemeral = True)

    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="off_ntf" , emoji="🔴" , row= 0)
    async def off_ntf_button (self , interaction:discord.interactions , button:discord.Button):            
        check = is_have_account(interaction.user.id)
        if check["have_account"] == True:        
            user_id = interaction.user.id
            await of_ntf(user_id= user_id , fun= "off")
            await interaction.response.send_message("**you have been turn off your notification🔴**",ephemeral = True)
        else:
            await interaction.response.send_message("**You don't Have Account Yet**" , ephemeral = True)


# -----------------------------{Posts -=> System}-----------------------------

async def check_post (user,message , lang):
    try:
        description = message.content
        if description == "":
            description = " "

        photo = message.attachments[0].url
        description = description.replace("`" , "" ,).replace("*" , "").replace("|" , "").replace("~" , "")
        await send_post(user= user ,description= description ,photo= photo ,lang= lang)

    except:
        await message.delete()

async def send_post(user , description , photo , lang) :
    #user embed request
    embedd2 = discord.Embed(colour=0x0070FF ,title=f"Your Post has been sent to admins :outbox_tray:  " , description=  f"Pending Post..   :pushpin:  ")
    embedd2.add_field(name="Status :yellow_circle::" , value=f"Waiting until admin accept or decline your post.." , inline=False)
    embedd2.set_footer(text=footer())
    await embed_ntf(user , embedd2)

    #admin embed request
    embedd = discord.Embed(colour=0x0070FF ,title=f"New Post Recived   :mailbox_with_mail: " , description=  f"Pending Post..   :pushpin:  ")
    embedd.add_field(name="User   :man_raising_hand:   :" , value=f"{user.mention}" , inline=False)
    embedd.add_field(name="lang  🌐 :" , value=f"``{lang}``" , inline=False)
    embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
    embedd.add_field(name="Photo Link   :link:  :" , value=f"``{photo}``" , inline=False)
    embedd.add_field(name="Photo   :frame_photo:  :" , value=f" <--->" , inline=False)
    embedd.set_image(url= photo)
    embedd.set_footer(text=footer())

    butony = Post_view(user= user , description= description , photo= photo , lang= lang)
    if lang == "ar":
        channel = await client.fetch_channel(admin_check_posts_room_ar)
        message_id = (await channel.send(embed = embedd  , view=butony )).id


    elif lang == "en":
        channel = await client.fetch_channel(admin_check_posts_room_en)
        message_id = (await channel.send(embed = embedd  , view=butony )).id

    cr.execute(f"insert into pending_posts(user_id , description , photo , message_id , lang) values(?,?,?,?,?)", (user.id , description , photo , message_id , lang ,))
    db.commit()





class Post_modal(discord.ui.Modal, title='Post_modal'):
    def __init__(self ,user = None,description = None ,photo= None ,message_id = None ,button_self = None ):
        self.user = user
        self.description = description
        self.photo = photo
        self.message_id = message_id
        self.button_self = button_self
        
        super().__init__(timeout=None)   

    reason = discord.ui.TextInput(label='Reason')
    async def on_submit(self, interaction: discord.Interaction):

        embedd = await post_embedd(fun= "can2" , description= self.description , photo= self.photo , reason= self.reason)

        await embed_ntf (self.user , embedd)

        # await self.user.send(embed = embedd , view= Seen())

        await interaction.response.edit_message(view=self.button_self)
        await interaction.message.delete()
        cr.execute(f"delete from pending_posts where message_id = '{self.message_id}'")
        db.commit()        
        await log(who= interaction.user , what= "New Post Canceled" , message= f"``{interaction.user.name}`` **Has declined post . reason :** ``{self.reason}``")


class Post_view(View):
    def __init__(self ,user = None,description = None ,photo= None  , lang = None):
        self.user = user
        self.description = description
        self.photo = photo
        self.lang = lang
        super().__init__(timeout=None)
        

    @discord.ui.button(label= "Claim", style=discord.ButtonStyle.gray, custom_id="Claim")
    async def claim_button (self , interaction:discord.interactions , button:discord.Button):
        accept_button = [x for x in self.children if x.custom_id == "accept" ][0]
        declin_button = [x for x in self.children if x.custom_id == "declin" ][0]
        accept_button.disabled = False
        declin_button.disabled = False  
        button.label = f"{interaction.user.name}"
        button.disabled = True
        self.user_claim = interaction.user.id
        await interaction.response.edit_message(view = self)

    @discord.ui.button(label= "accept", style=discord.ButtonStyle.green, custom_id="accept" , disabled= True )
    async def accept_button(self , interaction:discord.interactions , button:discord.Button):
        same_admin = ""
        bot_was_offline = ""
        message_id = interaction.message.id

        try:
            if  interaction.user.id == self.user_claim:
                same_admin = True
            else:
                same_admin = False

            cr.execute(f"select * from pending_posts where message_id = '{message_id}'")
            post = cr.fetchall()[0]
            user_id = int(post[0]) 
            self.user = await client.fetch_user(user_id)
            self.description = post[2]
            self.photo = post[3]
            self.lang = post[1]
        except:
            bot_was_offline = True
            cr.execute(f"select * from pending_posts where message_id = '{message_id}'")
            post = cr.fetchall()[0]
            user_id = int(post[0]) 
            self.user = await client.fetch_user(user_id)
            self.description = post[2]
            self.photo = post[3]
            self.lang = post[1]


        if  same_admin == True or bot_was_offline == True:
            post_id = await genrate_post_id()
                    
            admin_id = interaction.user.id

            cr.execute("select user_id ,photo from users_posts ")
            data = cr.fetchall()
            new_data = (str(self.user.id) , self.photo ) 
            
            if new_data not in data :

                #المنشور تم قبوله بشكل رسمي 
            
                embedd = await post_embedd(fun= "pub" ,post_id= post_id ,description= self.description ,photo= self.photo)
                await embed_ntf (self.user , embedd)
                # await self.user.send(embed = embedd , view= Seen())

                cr.execute(f"insert into users_posts(post_id , user_id ,admin_id, photo , description  , lang) values(?,?,?,?,?,?) ", (post_id,self.user.id ,admin_id ,self.photo , self.description , self.lang,))
                db.commit()
                ar_bluoz(user_id , 1 , "A")
            elif new_data in data:
                #المنشور موجود بالفعل
                embedd = await post_embedd(fun= "can" ,description= self.description ,photo= self.photo)
                await embed_ntf (self.user , embedd)

                # await self.user.send(embed = embedd , view= Seen())

            await interaction.response.edit_message(view = self)
            await interaction.message.delete()
            cr.execute(f"delete from pending_posts where message_id = '{message_id}'")
            db.commit()
            await log(who= interaction.user , what= "New Post Published" , message= f"``{interaction.user.name}`` **Has accepted this post** ``{post_id}``")
        else:
            await interaction.response.send_message(":x:  **Invalid** this post for another admin" ,ephemeral = True)


    @discord.ui.button(label= "decline", style=discord.ButtonStyle.red, custom_id="declin" ,disabled=True)
    async def decline_button(self , interaction:discord.interactions , button:discord.Button):
        same_admin = ""
        bot_was_offline = ""        
        message_id = interaction.message.id

        try:
            if  interaction.user.id == self.user_claim:
                same_admin = True
            else:
                same_admin = False
        except:
            bot_was_offline = True
            cr.execute(f"select * from pending_posts where message_id = '{message_id}'")
            post = cr.fetchall()[0]
            user_id = int(post[0]) 
            self.user = await client.fetch_user(user_id)
            self.description = post[1]
            self.photo = post[2]


        if same_admin == True or bot_was_offline == True :
            await interaction.response.send_modal(Post_modal(user= self.user,description= self.description ,photo= self.photo ,message_id= message_id ,button_self= self,))

        else:
            await interaction.response.send_message(":x:  **Invalid** this post for another admin" ,ephemeral = True)



async def check_watch_before(user_id = None , all = None):
    if user_id != None :
        cr.execute(f"select watch_message from registers_users where user_id = '{user_id}' ")
        watch_message = (cr.fetchall())
        cr.execute(f"update registers_users set watch_message = ' ' where user_id = '{user_id}'")
        db.commit()        


    elif all != None:
        cr.execute(f"select watch_message from registers_users")
        watch_message = (cr.fetchall())
        cr.execute(f"update registers_users set watch_message = ' ' ")
        db.commit()


    if (' ',) in watch_message :
        watch_message = [x for x in watch_message if x != (' ',)]
        if watch_message == [] :
            return 'True'

    for user in watch_message :
        watch_message_content = user[0].replace(" " , "").split(",")

        try:
            guild = await client.fetch_guild( int(watch_message_content[0]) )
            channel = await guild.fetch_channel( int(watch_message_content[1]) )
            message = await channel.fetch_message( int(watch_message_content[2]) )
            await message.delete()
        except:
            pass

        await asyncio.sleep(2)


    return 'True'






class Watch_select(View):
    def __init__ (self,channel,user):
        self.user = user
        self.channel = channel
        self.previous_posts = []
        self.current_post = 0

        super().__init__(timeout=None)   

    @discord.ui.select(
        placeholder="Choose a page" , 
        options=[
            discord.SelectOption(
                label = "Explore ",
                emoji = "🏠",
                value = "Explore" ,
            ),
            discord.SelectOption(
                label = "Following Only ",
                emoji = "<:followed:1032179554510438531>",
                value= "Following",
            ),
            discord.SelectOption(
                label = "Favorite Only ",
                emoji = "<:addedtofave:1032181367531905064>",
                value= "Favorite",
            )            
        ]

    )
    async def call_back(self , interaction:discord.interactions , select):
        if interaction.user.id == self.user.id:
            await interaction.response.send_message("**=================================================**")
            await interaction.delete_original_response()

            if select.values[0] == "Explore":
 
                await watch_explore_posts(interaction.message , self.user)

            elif select.values[0] == "Following":
                await watch_following_posts(interaction.message , self.user)


            elif select.values[0] == "Favorite":
                await watch_favorite_posts(interaction.message , self.user)



        else:
            #انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)


class Explore_watch_posts(View):
    def __init__ (self ,ctx ,user , current_post , previous_posts) :
        self.ctx = ctx
        self.user = user
        self.previous_posts = previous_posts
        self.favorite_posts = []
        self.reported_posted = []
        self.friend = []
        self.reactioned_posts = []
        self.current_post = current_post
        self.home_page = 0
        
        super().__init__(timeout=None)   




    @discord.ui.button(emoji="◀" , style=discord.ButtonStyle.gray, custom_id="eback" ,disabled= True )
    async def back_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            previous_post_id = self.previous_posts [(self.previous_posts.index(self.current_post) - 1)]
            self.current_post = previous_post_id
            self.home_page =  interaction.message 

            try:
                embedd = await post_with_id(previous_post_id , fun= "E")
            except:
                index = self.previous_posts.index(self.current_post)
                self.previous_posts.remove(self.current_post)

                if index != 0 :
                    self.current_post = self.previous_posts[index - 1]
                    post_id = self.current_post
                    embedd = await post_with_id(post_id , fun= "E")

                else:
                    button.disabled = True


            await self.home_page.edit(embed = embedd , view = self)
            if self.current_post == self.previous_posts[0] :
                button.disabled = True

            go_button = [x for x in self.children if x.custom_id == "ego" ][0]       
            favorite_button = [x for x in self.children if x.custom_id == "eadd_favorite" ][0]
            friend_button = [x for x in self.children if x.custom_id == "eadd_friend" ][0]                
            report_button = [x for x in self.children if x.custom_id == "ereport_post" ][0]                
            like_button = [x for x in self.children if x.custom_id == "elike" ][0]       
            haha_button = [x for x in self.children if x.custom_id == "ehaha" ][0]       
            sad_button = [x for x in self.children if x.custom_id == "esad" ][0]       


            if self.current_post in self.favorite_posts:
                favorite_button.emoji = "<:addedtofave:1032181367531905064>"
            else:
                favorite_button.emoji = "<:addtofave:1032181322954842152>"


            if self.current_post in self.friend:
                friend_button.disabled = True
                friend_button.emoji = "<:followed:1032179554510438531>"
                
            else:
                friend_button.disabled = False
                friend_button.emoji = "<:follow:1032179508557643796>"


            if self.current_post in self.reported_posted:
                report_button.disabled = True
            else:
                report_button.disabled = False


            if self.current_post in self.reactioned_posts:
                like_button.disabled = True
                haha_button.disabled = True
                sad_button.disabled = True
                like_button.label = ""
                haha_button.label = ""
                sad_button.label = ""

            else:
                like_button.disabled = False
                haha_button.disabled = False
                sad_button.disabled = False
                like_button.label = ""
                haha_button.label = ""
                sad_button.label = ""

            if self.current_post != 0 :
                go_button.disabled = False


            if self.current_post == 0 :
                favorite_button.disabled = True
            else:
                favorite_button.disabled = False


            await interaction.response.edit_message(view = self)

        else:
            #انت لست نفس الشخص 
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)



    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="elike" , emoji="❤")
    async def like_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.reactioned_posts:
                self.reactioned_posts.append(self.current_post)
                button.disabled = True
                await add_reaction(interaction.user , self.current_post , "like")
                like_reactions = await hm_reactions(self.current_post , "like")
                button.label = f"{like_reactions}"
                haha_button = [x for x in self.children if x.custom_id == "ehaha" ][0]       
                sad_button = [x for x in self.children if x.custom_id == "esad" ][0]
                haha_button.disabled = True
                sad_button.disabled = True                       
                await interaction.response.edit_message(view = self)        
                user_id2 = int(await get_user_from_post(self.current_post))
                await send_reaction_info(interaction.user.id , user_id2,self.current_post , "❤")


        else:
            #انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)



    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="ehaha" , emoji="😂")
    async def haha_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.reactioned_posts:
                self.reactioned_posts.append(self.current_post)
                button.disabled = True
                await add_reaction(interaction.user , self.current_post , "haha")
                like_reactions = await hm_reactions(self.current_post , "haha")
                button.label = f"{like_reactions}"
                like_button = [x for x in self.children if x.custom_id == "elike" ][0]       
                sad_button = [x for x in self.children if x.custom_id == "esad" ][0]
                like_button.disabled = True
                sad_button.disabled = True                          
                await interaction.response.edit_message(view = self)        
                user_id2 = int(await get_user_from_post(self.current_post))
                await send_reaction_info(interaction.user.id , user_id2,self.current_post , "😂")


        else:
            #انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)



    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="esad" , emoji="😢")
    async def sad_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.reactioned_posts:
                self.reactioned_posts.append(self.current_post)
                button.disabled = True
                await add_reaction(interaction.user , self.current_post , "sad")
                like_reactions = await hm_reactions(self.current_post , "sad")
                button.label = f"{like_reactions}"
                like_button = [x for x in self.children if x.custom_id == "elike" ][0]       
                haha_button = [x for x in self.children if x.custom_id == "ehaha" ][0]       
                like_button.disabled = True
                haha_button.disabled = True
                await interaction.response.edit_message(view = self)        
                user_id2 = int(await get_user_from_post(self.current_post))
                await send_reaction_info(interaction.user.id , user_id2,self.current_post , "😢")


        else:
            #انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)





    @discord.ui.button(emoji="▶" , style=discord.ButtonStyle.gray, custom_id="ego")
    async def go_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if (self.previous_posts == [] and self.current_post == 0) or self.current_post == self.previous_posts[-1]:
                post_id = await explore_post_id(self.user.id)
                if post_id != None :
                    embedd = await post_with_id(post_id , fun= "E")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 
                    await self.home_page.edit(embed = embedd , view = self)
                    # await add_view(post_id , self.user.id)
                else:
                    post_id = 0
                    embedd = await post_with_id(post_id , fun= "E")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 
                    await self.home_page.edit(embed = embedd , view = self)
                    button.disabled = True
                    
            else:
                next_post_id = self.previous_posts [(self.previous_posts.index(self.current_post) + 1)]
                self.current_post = next_post_id
                self.home_page =  interaction.message 

                try:
                    embedd = await post_with_id(next_post_id , fun= "E")

                except:
                    index = self.previous_posts.index(self.current_post)

                    if self.current_post != self.previous_posts[-1]:
                        self.previous_posts.remove(self.current_post)
                        self.current_post = self.previous_posts[index]
                        post_id = self.current_post
                        embedd = await post_with_id(post_id , fun= "E")
                        self.home_page =  interaction.message                     

                    else:
                        self.previous_posts.remove(self.current_post)
                        post_id = await explore_post_id(self.user.id)
                        if post_id != None :
                            embedd = await post_with_id(post_id , fun= "E")
                            self.previous_posts.append(post_id)
                            self.current_post = post_id
                            self.home_page =  interaction.message 
                        else:
                            post_id = 0
                            embedd = await post_with_id(post_id , fun= "Fav")
                            self.previous_posts.append(post_id)
                            self.current_post = post_id
                            self.home_page =  interaction.message 
                            await self.home_page.edit(embed = embedd , view = self)
                            button.disabled = True


                await self.home_page.edit(embed = embedd , view = self)





            back_button = [x for x in self.children if x.custom_id == "eback" ][0]                
            favorite_button = [x for x in self.children if x.custom_id == "eadd_favorite" ][0]
            friend_button = [x for x in self.children if x.custom_id == "eadd_friend" ][0]                
            report_button = [x for x in self.children if x.custom_id == "ereport_post" ][0]                
            like_button = [x for x in self.children if x.custom_id == "elike" ][0]       
            haha_button = [x for x in self.children if x.custom_id == "ehaha" ][0]       
            sad_button = [x for x in self.children if x.custom_id == "esad" ][0]       

            if self.current_post != self.previous_posts[0] and back_button.disabled == True:
                back_button.disabled = False


            if self.current_post in self.favorite_posts:
                favorite_button.emoji = "<:addedtofave:1032181367531905064>"

            else:
                favorite_button.emoji = "<:addtofave:1032181322954842152>"


            if self.current_post in self.friend or self.current_post == 0:
                friend_button.disabled = True
                friend_button.emoji = "<:followed:1032179554510438531>"

            else:
                friend_button.disabled = False
                friend_button.emoji = "<:follow:1032179508557643796>"                

            if self.current_post in self.reported_posted or self.current_post == 0:
                report_button.disabled = True
            else:
                report_button.disabled = False



            if self.current_post in self.reactioned_posts or self.current_post == 0:
                like_button.disabled = True
                haha_button.disabled = True
                sad_button.disabled = True
                like_button.label = ""
                haha_button.label = ""
                sad_button.label = ""

            else:
                like_button.disabled = False
                haha_button.disabled = False
                sad_button.disabled = False
                like_button.label = ""
                haha_button.label = ""
                sad_button.label = ""

            if self.current_post == 0 :
                favorite_button.disabled = True
                button.disabled = True
            else:
                favorite_button.disabled = False


            await interaction.response.edit_message(view = self)

        else:
            # انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)


    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="eadd_favorite" , emoji="<:addtofave:1032181322954842152>" , row= 1)
    async def add_favorite_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :

            check =  await check_favorite(user_id= self.user.id , post_id= self.current_post)
            if check == False:
                self.favorite_posts.append(self.current_post)
                button.emoji = "<:addedtofave:1032181367531905064>"
                await interaction.response.edit_message(view = self)
                await ar_favorite(fun="A" , user_id= self.user.id , post_id= self.current_post)

            elif check == True:
                self.favorite_posts.remove(self.current_post)
                button.emoji = "<:addtofave:1032181322954842152>"
                await interaction.response.edit_message(view = self)
                await ar_favorite(fun="R" , user_id=self.user.id , post_id=self.current_post)
        else:
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)
            #انت لست نفس الشسخص

    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="eadd_friend" , emoji="<:follow:1032179508557643796>" , row=1)
    async def ar_friend_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.friend :
                user2_id = await get_user_from_post(self.current_post)
                user1_id = self.user.id
                check = await check_follower(user1_id=user1_id , user2_id=user2_id)
                if check == False:
                    button.disabled = True
                    button.emoji = "<:followed:1032179554510438531>"
                    await interaction.response.edit_message (view = self)
                    await sr_follow_info(fun="S" , user1_id= user1_id , user2_id= user2_id)
                    await ar_follow(user1_id= user1_id , user2_id= user2_id , fun="A")
                    self.friend.append(self.current_post)

                else:
                    button.disabled = True
                    button.emoji = "<:followed:1032179554510438531>"
                    await interaction.response.edit_message (view = self)
                    self.friend.append(self.current_post)

            

        else:
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)
            #انت لست نفس الشخص



    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="ereport_post" , emoji="⚠" , row=1)
    async def report_post_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.reported_posted:
                await report_post(post_id= self.current_post , user_id= self.user.id)
                self.reported_posted.append(self.current_post)
                index = self.previous_posts.index(self.current_post)
                self.previous_posts.remove(self.current_post)
                if index != 0:
                    self.current_post = self.previous_posts[index - 1]
                    post_id = self.current_post
                    embedd = await post_with_id(post_id , fun= "E")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 

                else:
                    post_id = await explore_post_id(self.user.id)
                    self.current_post = post_id
                    embedd = await post_with_id(post_id , fun= "E")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 

                await interaction.response.edit_message(embed = embedd,view = self)
        

        else:
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)
            



class Friend_watch_posts(View):
    def __init__ (self ,ctx ,user , current_post , previous_posts) :
        self.ctx = ctx
        self.user = user
        self.previous_posts = previous_posts
        self.favorite_posts = []
        self.reported_posted = []
        self.reactioned_posts = []
        self.current_post = current_post
        self.home_page = 0
        
        super().__init__(timeout=None)   




    @discord.ui.button(emoji="◀" , style=discord.ButtonStyle.gray, custom_id="fback" ,disabled= True )
    async def back_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            previous_post_id = self.previous_posts [(self.previous_posts.index(self.current_post) - 1)]
            self.current_post = previous_post_id
            self.home_page =  interaction.message 

            try:
                embedd = await post_with_id(previous_post_id , fun= "F")
            except:
                index = self.previous_posts.index(self.current_post)
                self.previous_posts.remove(self.current_post)

                if index != 0 :
                    self.current_post = self.previous_posts[index - 1]
                    post_id = self.current_post
                    embedd = await post_with_id(post_id , fun= "F")

                else:
                    button.disabled = True


            await self.home_page.edit(embed = embedd , view = self)
            if self.current_post == self.previous_posts[0] :
                button.disabled = True

            go_button = [x for x in self.children if x.custom_id == "fgo" ][0]       
            favorite_button = [x for x in self.children if x.custom_id == "fadd_favorite" ][0]
            report_button = [x for x in self.children if x.custom_id == "freport_post" ][0]                
            like_button = [x for x in self.children if x.custom_id == "flike" ][0]       
            haha_button = [x for x in self.children if x.custom_id == "fhaha" ][0]       
            sad_button = [x for x in self.children if x.custom_id == "fsad" ][0]       


            if self.current_post in self.favorite_posts:
                favorite_button.emoji = "<:addedtofave:1032181367531905064>"
            else:
                favorite_button.emoji = "<:addtofave:1032181322954842152>"


            if self.current_post in self.reported_posted:
                report_button.disabled = True
            else:
                report_button.disabled = False


            if self.current_post in self.reactioned_posts:
                like_button.disabled = True
                haha_button.disabled = True
                sad_button.disabled = True
                like_button.label = ""
                haha_button.label = ""
                sad_button.label = ""

            else:
                like_button.disabled = False
                haha_button.disabled = False
                sad_button.disabled = False
                like_button.label = ""
                haha_button.label = ""
                sad_button.label = ""

            if self.current_post != 0 :
                go_button.disabled = False


            if self.current_post == 0 :
                favorite_button.disabled = True
            else:
                favorite_button.disabled = False


            await interaction.response.edit_message(view = self)

        else:
            #انت لست نفس الشخص 
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)



    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="flike" , emoji="❤")
    async def like_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.reactioned_posts:
                self.reactioned_posts.append(self.current_post)
                button.disabled = True
                await add_reaction(interaction.user , self.current_post , "like")
                like_reactions = await hm_reactions(self.current_post , "like")
                button.label = f"{like_reactions}"
                haha_button = [x for x in self.children if x.custom_id == "fhaha" ][0]       
                sad_button = [x for x in self.children if x.custom_id == "fsad" ][0]
                haha_button.disabled = True
                sad_button.disabled = True                       
                await interaction.response.edit_message(view = self)        
                user_id2 = int(await get_user_from_post(self.current_post))
                await send_reaction_info(interaction.user.id , user_id2,self.current_post , "❤")


        else:
            #انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)



    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="fhaha" , emoji="😂")
    async def haha_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.reactioned_posts:
                self.reactioned_posts.append(self.current_post)
                button.disabled = True
                await add_reaction(interaction.user , self.current_post , "haha")
                like_reactions = await hm_reactions(self.current_post , "haha")
                button.label = f"{like_reactions}"
                like_button = [x for x in self.children if x.custom_id == "flike" ][0]       
                sad_button = [x for x in self.children if x.custom_id == "fsad" ][0]
                like_button.disabled = True
                sad_button.disabled = True                          
                await interaction.response.edit_message(view = self)        
                user_id2 = int(await get_user_from_post(self.current_post))
                await send_reaction_info(interaction.user.id , user_id2,self.current_post , "😂")


        else:
            #انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)



    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="fsad" , emoji="😢")
    async def sad_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.reactioned_posts:
                self.reactioned_posts.append(self.current_post)
                button.disabled = True
                await add_reaction(interaction.user , self.current_post , "sad")
                like_reactions = await hm_reactions(self.current_post , "sad")
                button.label = f"{like_reactions}"
                like_button = [x for x in self.children if x.custom_id == "flike" ][0]       
                haha_button = [x for x in self.children if x.custom_id == "fhaha" ][0]       
                like_button.disabled = True
                haha_button.disabled = True
                await interaction.response.edit_message(view = self)        
                user_id2 = int(await get_user_from_post(self.current_post))
                await send_reaction_info(interaction.user.id , user_id2,self.current_post , "😢")


        else:
            #انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)





    @discord.ui.button(emoji="▶" , style=discord.ButtonStyle.gray, custom_id="fgo")
    async def go_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if (self.previous_posts == [] and self.current_post == 0) or self.current_post == self.previous_posts[-1]:
                post_id = await explore_post_id(self.user.id)
                if post_id != None :
                    embedd = await post_with_id(post_id , fun= "F")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 
                    await self.home_page.edit(embed = embedd , view = self)
                    # await add_view(post_id , self.user.id)
                else:
                    post_id = 0
                    embedd = await post_with_id(post_id , fun= "F")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 
                    await self.home_page.edit(embed = embedd , view = self)
                    button.disabled = True
                    
            else:
                next_post_id = self.previous_posts [(self.previous_posts.index(self.current_post) + 1)]
                self.current_post = next_post_id
                self.home_page =  interaction.message 

                try:
                    embedd = await post_with_id(next_post_id , fun= "F")

                except:
                    index = self.previous_posts.index(self.current_post)

                    if self.current_post != self.previous_posts[-1]:
                        self.previous_posts.remove(self.current_post)
                        self.current_post = self.previous_posts[index]
                        post_id = self.current_post
                        embedd = await post_with_id(post_id , fun= "F")
                        self.home_page =  interaction.message                     

                    else:
                        self.previous_posts.remove(self.current_post)
                        post_id = await following_post_id(self.user.id)
                        if post_id != None :
                            embedd = await post_with_id(post_id , fun= "F")
                            self.previous_posts.append(post_id)
                            self.current_post = post_id
                            self.home_page =  interaction.message 
                        else:
                            post_id = 0
                            embedd = await post_with_id(post_id , fun= "Fav")
                            self.previous_posts.append(post_id)
                            self.current_post = post_id
                            self.home_page =  interaction.message 
                            await self.home_page.edit(embed = embedd , view = self)
                            button.disabled = True

                await self.home_page.edit(embed = embedd , view = self)



            back_button = [x for x in self.children if x.custom_id == "fback" ][0]                
            favorite_button = [x for x in self.children if x.custom_id == "fadd_favorite" ][0]
            report_button = [x for x in self.children if x.custom_id == "freport_post" ][0]                
            like_button = [x for x in self.children if x.custom_id == "flike" ][0]       
            haha_button = [x for x in self.children if x.custom_id == "fhaha" ][0]       
            sad_button = [x for x in self.children if x.custom_id == "fsad" ][0]       

            if self.current_post != self.previous_posts[0] and back_button.disabled == True:
                back_button.disabled = False


            if self.current_post in self.favorite_posts:
                favorite_button.emoji = "<:addedtofave:1032181367531905064>"

            else:
                favorite_button.emoji = "<:addtofave:1032181322954842152>"


            if self.current_post in self.reported_posted or self.current_post == 0:
                report_button.disabled = True
            else:
                report_button.disabled = False



            if self.current_post in self.reactioned_posts or self.current_post == 0:
                like_button.disabled = True
                haha_button.disabled = True
                sad_button.disabled = True
                like_button.label = ""
                haha_button.label = ""
                sad_button.label = ""

            else:
                like_button.disabled = False
                haha_button.disabled = False
                sad_button.disabled = False
                like_button.label = ""
                haha_button.label = ""
                sad_button.label = ""

            if self.current_post == 0 :
                favorite_button.disabled = True
                button.disabled = True
            else:
                favorite_button.disabled = False


            await interaction.response.edit_message(view = self)

        else:
            # انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)


    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="fadd_favorite" , emoji="<:addtofave:1032181322954842152>" , row= 1)
    async def add_favorite_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :

            check =  await check_favorite(user_id= self.user.id , post_id= self.current_post)
            if check == False:
                self.favorite_posts.append(self.current_post)
                button.emoji = "<:addedtofave:1032181367531905064>"
                await interaction.response.edit_message(view = self)
                await ar_favorite(fun="A" , user_id= self.user.id , post_id= self.current_post)

            elif check == True:
                self.favorite_posts.remove(self.current_post)
                button.emoji = "<:addtofave:1032181322954842152>"
                await interaction.response.edit_message(view = self)
                await ar_favorite(fun="R" , user_id=self.user.id , post_id=self.current_post)
        else:
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)
            #انت لست نفس الشسخص


    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="freport_post" , emoji="⚠" , row=1)
    async def report_post_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            if self.current_post not in self.reported_posted:
                await report_post(post_id= self.current_post , user_id= self.user.id)
                self.reported_posted.append(self.current_post)
                index = self.previous_posts.index(self.current_post)
                self.previous_posts.remove(self.current_post)
                if index != 0:
                    self.current_post = self.previous_posts[index - 1]
                    post_id = self.current_post
                    embedd = await post_with_id(post_id , fun= "F")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 

                else:
                    post_id = await explore_post_id(self.user.id)
                    self.current_post = post_id
                    embedd = await post_with_id(post_id , fun= "F")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message

                await interaction.response.edit_message(view = self)

        else:
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)
            



class Favorite_watch_posts(View):
    def __init__ (self ,ctx ,user , current_post , previous_posts) :
        self.ctx = ctx
        self.user = user
        self.previous_posts = previous_posts
        self.favorite_posts = []
        self.current_post = current_post
        self.home_page = 0
        
        super().__init__(timeout=None)   




    @discord.ui.button(emoji="◀" , style=discord.ButtonStyle.gray, custom_id="vback" ,disabled= True )
    async def back_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
            previous_post_id = self.previous_posts [(self.previous_posts.index(self.current_post) - 1)]
            self.current_post = previous_post_id
            self.home_page =  interaction.message 

            embedd = await post_with_id(previous_post_id , fun= "Fav")
            await self.home_page.edit(embed = embedd , view = self)


            if self.current_post == self.previous_posts[0] :
                button.disabled = True



            go_button = [x for x in self.children if x.custom_id == "vgo" ][0]       
            favorite_button = [x for x in self.children if x.custom_id == "vadd_favorite" ][0]


            if self.current_post in self.favorite_posts:
                favorite_button.emoji ="<:addtofave:1032181322954842152>"
            else:
                favorite_button.emoji = "<:addedtofave:1032181367531905064>"


            if self.current_post != 0 :
                go_button.disabled = False


            if self.current_post == 0 :
                favorite_button.disabled = True
            else:
                favorite_button.disabled = False


            await interaction.response.edit_message(view = self)

        else:
            #انت لست نفس الشخص 
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)



    @discord.ui.button(label="" , style=discord.ButtonStyle.gray, custom_id="vadd_favorite" , emoji="<:addedtofave:1032181367531905064>" , row= 0)
    async def add_favorite_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :

            check =  await check_favorite(user_id= self.user.id , post_id= self.current_post)
            if check == True:
                self.favorite_posts.append(self.current_post)
                button.emoji = "<:addtofave:1032181322954842152>"
                await interaction.response.edit_message(view = self)
                await ar_favorite(fun="R" , user_id= self.user.id , post_id= self.current_post)

            elif check == False:
                self.favorite_posts.remove(self.current_post)
                button.emoji = "<:addedtofave:1032181367531905064>"
                await interaction.response.edit_message(view = self)
                await ar_favorite(fun="A" , user_id=self.user.id , post_id=self.current_post)
        else:
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)
            #انت لست نفس الشسخص




    @discord.ui.button(emoji="▶" , style=discord.ButtonStyle.gray, custom_id="vgo")
    async def go_button (self , interaction:discord.interactions , button:discord.Button):
        if interaction.user.id == self.user.id :
             
            if (self.previous_posts == [] and self.current_post == 0) or self.current_post == self.previous_posts[-1]:
                num = len(self.previous_posts) + 1
                post_id = await favorite_post_id(self.user.id , num)
                if post_id != None :
                    embedd = await post_with_id(post_id , fun= "Fav")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 
                    await self.home_page.edit(embed = embedd , view = self)
                    # await add_view(post_id , self.user.id)
                else:
                    post_id = 0
                    embedd = await post_with_id(post_id , fun= "Fav")
                    self.previous_posts.append(post_id)
                    self.current_post = post_id
                    self.home_page =  interaction.message 
                    await self.home_page.edit(embed = embedd , view = self)
                    button.disabled = True
                    
            else:
                next_post_id = self.previous_posts [(self.previous_posts.index(self.current_post) + 1)]
                self.current_post = next_post_id
                self.home_page =  interaction.message 
                embedd = await post_with_id(next_post_id , fun= "Fav")
                await self.home_page.edit(embed = embedd , view = self)


            back_button = [x for x in self.children if x.custom_id == "vback" ][0]                
            favorite_button = [x for x in self.children if x.custom_id == "vadd_favorite" ][0]

            if self.current_post != self.previous_posts[0] and back_button.disabled == True:
                back_button.disabled = False


            if self.current_post in self.favorite_posts:
                favorite_button.emoji = "<:addtofave:1032181322954842152>"

            else:
                favorite_button.emoji = "<:addedtofave:1032181367531905064>"


            if self.current_post == 0 :
                favorite_button.disabled = True
                button.disabled = True
            else:
                favorite_button.disabled = False


            await interaction.response.edit_message(view = self)
        else:
            # انت لست نفس الشخص
            await interaction.response.send_message(":x:  **Invalid** this not ur account" ,ephemeral = True)



async def post_embedd(fun =None, post_id =None, description =None, photo =None, reason = None):
    if fun == "pub":
        embedd = discord.Embed(colour=0x0070FF ,title=f"Your Post has been published ✔" , description=  f"")
        embedd.add_field(name="Status :green_circle::" , value=f"admin has been check your post and accepted it" , inline=False)
        embedd.add_field(name="Post id :" , value=f"``{post_id}``" , inline=False)
        embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
        embedd.add_field(name="Photo   :frame_photo:  :" , value=f" <--->" , inline=False)
        embedd.set_image(url= photo)
        embedd.set_footer(text=footer())
        return embedd
    elif fun == "can1":
        embedd = discord.Embed(colour=0x0070FF ,title=f"Your Post has been canceled ❌" , description=  f"")
        embedd.add_field(name="Status :red_circle::" , value=f"admin has been check your post and canceled it" , inline=False)
        embedd.add_field(name="Reason :" , value=f"``The post you have been sent already exit``" , inline=False)
        embedd.set_footer(text=footer())
        embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
        embedd.add_field(name="Photo   :frame_photo:  :" , value=f" <--->" , inline=False)
        embedd.set_image(url= photo)        
        return embedd

    elif fun == "can2":
        embedd = discord.Embed(colour=0x0070FF ,title=f"Your Post has been canceled ❌" , description=  f"")
        embedd.add_field(name="Status :red_circle::" , value=f"admin has been check your post and canceled it" , inline=False)
        embedd.add_field(name="Reason :" , value=f"``{reason}``" , inline=False)
        embedd.set_footer(text=footer())
        embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
        embedd.add_field(name="Photo   :frame_photo:  :" , value=f" <--->" , inline=False)
        embedd.set_image(url= photo)        
        return embedd



async def genrate_post_id():
        post_id = random.choice(range(100000,999999))
        post_as_table =  (str(post_id),)
        cr.execute("select post_id from users_posts")
        posts_id_db = cr.fetchall()
        if post_as_table not in posts_id_db:
            return post_id
        else:
            await genrate_post_id()

async def post_with_id(post_id  , fun = None): 
    cr.execute(f"select user_id,description,photo,activity,admin_id from users_posts where post_id ='{post_id}' ")
    explore_post = cr.fetchone()    
    user = await client.fetch_user(int(explore_post[0]))
    admin = await client.fetch_user(int(explore_post[4]))
    description = explore_post[1]
    photo = explore_post[2]
    activity = explore_post[3]
    rank = (await get_rule_from_id(explore_post[0])).capitalize()
    username = await get_username_from_id(explore_post[0])
    if fun == "E":
        embedd = discord.Embed(colour=0x0070FF ,title=f"Explore Page 🏠" , description=  f"")
        embedd.add_field(name=f"{rank}   :man_raising_hand:   :" , value=f"``{username}``" , inline=False)
        embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
        embedd.set_image(url= photo)
        embedd.set_thumbnail(url=user.display_avatar.url)
        embedd.set_footer(text=footer())
        return embedd

    elif fun == "F":
        embedd = discord.Embed(colour=0x0070FF ,title=f"Following Page <:followed:1032179554510438531> " , description=  f"")
        embedd.add_field(name=f"{rank}   :man_raising_hand:   :" , value=f"``{username}``" , inline=False)
        embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
        embedd.set_image(url= photo)
        embedd.set_thumbnail(url=user.display_avatar.url)
        embedd.set_footer(text=footer())
        return embedd

    elif fun == "Fav":
        embedd = discord.Embed(colour=0x0070FF ,title=f"Favorite Page <:addedtofave:1032181367531905064> " , description=  f"")
        embedd.add_field(name=f"{rank}   :man_raising_hand:   :" , value=f"``{username}``" , inline=False)
        embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
        embedd.set_image(url= photo)
        embedd.set_thumbnail(url=user.display_avatar.url)
        embedd.set_footer(text=footer())
        return embedd

    elif fun == "R":
        embedd = discord.Embed(colour=0x0070FF ,title=f"reported post ⚠" , description=  f"")
        embedd.add_field(name="Admin   :man_raising_hand:   :" , value=f"{admin.mention}" , inline=False)
        embedd.add_field(name="User   :man_raising_hand:   :" , value=f"{user.mention}" , inline=False)
        embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
        embedd.set_image(url= photo)
        embedd.set_thumbnail(url=user.display_avatar.url)
        embedd.set_footer(text=footer())        
        return embedd

    elif fun == "V":
        embedd = discord.Embed(colour=0x0070FF ,title=f"View Page 🎞" , description=  f"")
        embedd.add_field(name=f"{rank}   :man_raising_hand:   :" , value=f"``{username}``" , inline=False)
        embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
        embedd.set_image(url= photo)
        embedd.set_thumbnail(url=user.display_avatar.url)
        embedd.set_footer(text=footer())
        return embedd

async def add_view(post_id , user_id):
    cr.execute(f"update users_posts set views = (views || '\n{user_id}') where  post_id = '{post_id}' ")
    db.commit()


async def get_views(post_id):
    try:
        cr.execute("select views from users_posts where post_id = ? " , (post_id,))
        views = cr.fetchone()[0]
        views_post_num = (len(views.replace("\r" , "").split("\n"))) - 1    
        return views_post_num
    except:
        return 0 

async def explore_post_id(user_id):
    lang = await get_lang_from_id(user_id)
    posts = []
    cr.execute(f"select post_id from users_posts where views not like '%{user_id}%' and user_id != '{user_id}' and post_id != '{0}' and lang like '%{lang}%' order by activity desc")
    trend_posts = cr.fetchmany(6)
    rand_posts = []    
    for post_id in trend_posts:
        posts.append(int(post_id[0]))
    posts = tuple(posts)

    try:
        cr.execute(f"select post_id from users_posts where views not like '%{user_id}%' and post_id not in {posts} and user_id != '{user_id}' and post_id != '{0}' and lang like '%{lang}%' order by Random()")
        rand_posts = cr.fetchmany(4)
    except:
        pass

    posts = list(posts)
    for post_id in rand_posts:
        posts.append(int(post_id[0]))

    try:
        explore_post_id = random.choice(posts)
        await add_view(explore_post_id , user_id)
    except:
        return None
    
    return explore_post_id


async def watch_explore_posts(ctx , user):
    previous_posts = []
    current_post = 0
    post_id = await explore_post_id(user.id)
    if post_id != None :
        embedd = await post_with_id(post_id , fun="E")
        previous_posts.append(post_id)
        current_post = post_id
        watch_message = await ctx.edit(content =  f"{user.mention}",embed = embedd ,view = Explore_watch_posts(ctx ,user ,current_post ,previous_posts))

        # await add_view(post_id ,user.id)
    else:
        post_id = '0'
        embedd = await post_with_id(post_id , fun="E")
        previous_posts.append(post_id)
        current_post = post_id
        watch_message = await ctx.edit( content = f"{user.mention}",embed = embedd , view = Seen())




async def following_post_id(user_id):
    lang = await get_lang_from_id(user_id)
    posts = []
    following =await get_following(user_id)
    if following == None:
        return None
    cr.execute(f"select post_id from users_posts where views not like '%{user_id}%' and user_id != '{user_id}' and post_id != '{0}' and user_id in {following} and lang like '%{lang}%' order by activity desc")
    trend_posts = cr.fetchmany(6)
    rand_posts = []    
    for post_id in trend_posts:
        posts.append(int(post_id[0]))
    posts = tuple(posts)

    try:
        cr.execute(f"select post_id from users_posts where views not like '%{user_id}%' and post_id not in {posts} and user_id != '{user_id}' and post_id != '{0}' and user_id in {following} and lang like '%{lang}%' order by Random()")
        rand_posts = cr.fetchmany(4)
    except:
        pass

    posts = list(posts)
    for post_id in rand_posts:
        posts.append(int(post_id[0]))

    try:
        following_post_id = random.choice(posts)
        await add_view(following_post_id , user_id)

    except:
        return None

    return following_post_id



async def watch_following_posts(ctx , user):
    previous_posts = []
    current_post = 0
    post_id = await following_post_id(user.id)
    if post_id != None :
        embedd = await post_with_id(post_id , fun="F")
        previous_posts.append(post_id)
        current_post = post_id
        watch_message = await ctx.edit( content = f"{user.mention}",embed = embedd ,view = Friend_watch_posts(ctx ,user ,current_post ,previous_posts))

        # await add_view(post_id ,user.id)
    else:
        post_id = '0'
        embedd = await post_with_id(post_id , fun="F")
        previous_posts.append(post_id)
        current_post = post_id
        watch_message = await ctx.edit( content = f"{user.mention}",embed = embedd , view = Seen())





async def favorite_post_id(user_id , num = None):
    try:
        posts = []
        cr.execute(f"select favorite_posts from registers_users where user_id = '{user_id}'")
        favorite_posts = cr.fetchone()[0]
        favorite_posts = ((favorite_posts.replace("\r" , "").split("\n"))[1:])
        favorite_post = favorite_posts[-num]
        return favorite_post
    except:
        return None





async def check_favorite(post_id = None , user_id = None):
        cr.execute(f"select favorite_posts from registers_users where user_id = '{user_id}' and favorite_posts not like '%{post_id}%' ")
        check = cr.fetchone()
        if check == None :
            return True
        else:
            return False

async def ar_favorite(post_id = None , user_id = None , fun = None):
    if fun == "A":
        cr.execute(f"update registers_users set favorite_posts = (favorite_posts || '\n{post_id}') where user_id = '{user_id}' ")
        db.commit()

    if fun == "R":
        cr.execute(f"update registers_users set favorite_posts = replace(favorite_posts , '\n{post_id}'  , '') where user_id = '{user_id}' ")
        db.commit()
    pass



async def watch_favorite_posts(ctx , user):
    previous_posts = []
    current_post = 0
    post_id = await favorite_post_id(user.id , 1)
    if post_id != None :
        embedd = await post_with_id(post_id , fun="Fav")
        previous_posts.append(post_id)
        current_post = post_id
        watch_message = await ctx.edit(content =  f"{user.mention}",embed = embedd ,view = Favorite_watch_posts(ctx ,user ,current_post ,previous_posts))

        # await add_view(post_id ,user.id)
    else:
        post_id = '0'
        embedd = await post_with_id(post_id , fun="Fav")
        previous_posts.append(post_id)
        current_post = post_id
        watch_message = await ctx.edit( content = f"{user.mention}",embed = embedd , view = Seen())


async def check_follower(fun = None ,user1_id =None , user2_id = None  ):
    if fun == None:
        cr.execute(f"select following from registers_users where user_id = '{user1_id}' and following like '%{user2_id}%'")
        user1 = cr.fetchone()
        if user1 != None :
            return True

        else:
            return False

    elif fun == "All":
        cr.execute(f"select followers from registers_users where user_id = '{user1_id}'")
        user_friends = cr.fetchone()[0]
        user_friends = (user_friends.replace("\r" , "").split("\n"))
        return user_friends

async def ar_follow(user1_id , user2_id ,fun = None):
    if fun == "A":
        cr.execute(f"update registers_users set following = (following || '\n{user2_id}') where user_id = '{user1_id}'")
        cr.execute(f"update registers_users set followers = (followers || '\n{user1_id}') where user_id = '{user2_id}'")
        ar_bluoz(user1_id , 1 , "A")
        ar_bluoz(user2_id , 1 , "A")


    elif fun == "R":
        cr.execute(f"update registers_users set following = replace(following  ,'\n{user2_id}' , '') where user_id = '{user1_id}'")
        cr.execute(f"update registers_users set followers = replace(followers  ,'\n{user1_id}' , '') where user_id = '{user2_id}'")
        ar_bluoz(user1_id , 1 , "R")
        ar_bluoz(user2_id , 1 , "R")


    db.commit()

async def sr_follow_info(fun = None , user1_id = None , user2_id = None):

    if fun == "S":
        user1 = await client.fetch_user(user1_id)
        user2 = await client.fetch_user(user2_id)
        username1 = await get_username_from_id(user1_id)
        embedd = discord.Embed(colour=0x0070FF ,title=f"New follower recived   :mailbox_with_mail: " , description=  f"``{username1}`` started following you")
        embedd.set_thumbnail(url= user1.display_avatar.url)
        await embed_ntf (user2 , embedd)

        # await user2.send(embed = embedd , view= Seen())

async def get_following(user_id, fun = None):

    try:
        cr.execute(f"select following from registers_users where user_id = '{user_id}' ")
        following = tuple(((cr.fetchone()[0]).replace("\r" , "")).split("\n"))
        if following == (" ",):
            if fun == "num":
                return 0 
            return None  
        else:
            if fun == "num":
                return (len(following)) - 1 
            return following  
    except:
        if fun == "num":
            return 0
        return None



async def get_followers(user_id , fun = None):
    try:
        cr.execute(f"select followers from registers_users where user_id = '{user_id}' ")
        followers = tuple(((cr.fetchone()[0]).replace("\r" , "")).split("\n"))
        if followers == (" ",):
            if fun == "num":
                return 0             
            return None  
        else:
            if fun == "num":
                return (len(followers)) - 1            
            return followers  
    except:
        if fun == "num":
            return 0         
        return None



class report_view(View):
    def __init__(self ,post_id = None,):
        self.post_id = post_id
        super().__init__(timeout=None)
        

    @discord.ui.button(label= "Claim", style=discord.ButtonStyle.gray, custom_id="Claim2")
    async def claim_button (self , interaction:discord.interactions , button:discord.Button):
        accept_button = [x for x in self.children if x.custom_id == "delete_post" ][0]
        declin_button = [x for x in self.children if x.custom_id == "cancel_report" ][0]
        accept_button.disabled = False
        declin_button.disabled = False  
        button.label = f"{interaction.user.name}"
        button.disabled = True
        self.user_claim = interaction.user.id
        await interaction.response.edit_message(view = self)

    @discord.ui.button(label= "delete_post", style=discord.ButtonStyle.green, custom_id="delete_post" , disabled= True )
    async def delete_button(self , interaction:discord.interactions , button:discord.Button):
        try:
            check = self.user_claim
        except:
            self.user_claim = None

        if  interaction.user.id == self.user_claim or self.user_claim == None:
            await interaction.message.delete()
            cr.execute(f"delete from reported_posts where post_id = '{self.post_id}'")
            cr.execute(f"delete from users_posts where post_id = '{self.post_id}'")
        else:
            await interaction.response.send_message(":x:  **Invalid** this post for another admin" ,ephemeral = True)
        db.commit()

    @discord.ui.button(label= "cancel_report", style=discord.ButtonStyle.red, custom_id="cancel_report" ,disabled=True)
    async def cancel_button(self , interaction:discord.interactions , button:discord.Button):
        try:
            check = self.user_claim
        except:
            self.user_claim = None


        if  interaction.user.id == self.user_claim or self.user_claim == None:
            await interaction.message.delete()
            cr.execute(f"delete from reported_posts where post_id = '{self.post_id}'")
        else:
            await interaction.response.send_message(":x:  **Invalid** this post for another admin" ,ephemeral = True)
        db.commit()


async def report_post(post_id , user_id):
    cr.execute(f"select post_id from reported_posts where post_id = '{post_id}'")
    check = cr.fetchone()
    if check == None:
        embedd = await post_with_id(post_id= post_id , fun="R")
        channel = client.get_channel(report_channel)
        vieww = report_view(post_id= post_id)
        message = await channel.send(embed = embedd , view= vieww)
        cr.execute(f"insert into reported_posts(post_id , users_ids ,message_id) values('{post_id}' , '{user_id}' , '{message.id}')")
        db.commit()
    elif check != None :
        cr.execute(f"update reported_posts set users_ids = (users_ids || '\n{user_id}') where post_id = '{post_id}' ")
        db.commit()


async def add_reaction(user,post_id,reaction):
    if reaction == "like":
        cr.execute(f"update users_posts set like_reaction = (like_reaction || '\n{user.id}') where post_id = '{post_id}'")
        cr.execute(f"update users_posts set activity = (activity + 1 ) where post_id = '{post_id}'")

    elif reaction == "haha":
        cr.execute(f"update users_posts set haha_reaction = (haha_reaction || '\n{user.id}') where post_id = '{post_id}'")
        cr.execute(f"update users_posts set activity = (activity + 1 ) where post_id = '{post_id}'")


    elif reaction == "sad":
        cr.execute(f"update users_posts set sad_reaction = (sad_reaction || '\n{user.id}') where post_id = '{post_id}'")
        cr.execute(f"update users_posts set activity = (activity + 1 ) where post_id = '{post_id}'")

    ar_bluoz(user.id , 1 , "A")


    db.commit()
    pass


async def hm_reactions(post_id , reaction):
    try:
        if reaction == "like":
            cr.execute(f"select like_reaction from users_posts where post_id = '{post_id}'")
            reactions = cr.fetchone()[0]
            reactions = reactions.replace("\r" , "").replace(" " , "").split("\n")
            reactions_num = len(reactions) - 1
            return reactions_num

        elif reaction == "haha":
            cr.execute(f"select haha_reaction from users_posts where post_id = '{post_id}'")
            reactions = cr.fetchone()[0]
            reactions = reactions.replace("\r" , "").replace(" " , "").split("\n")
            reactions_num = len(reactions) - 1
            return reactions_num


        elif reaction == "sad":
            cr.execute(f"select sad_reaction from users_posts where post_id = '{post_id}'")
            reactions = cr.fetchone()[0]
            reactions = reactions.replace("\r" , "").replace(" " , "").split("\n")
            reactions_num = len(reactions) - 1
            return reactions_num
    except:
        return 0


async def send_reaction_info(user1_id ,user2_id ,post_id ,reaction):
    user1 = await client.fetch_user(user1_id)
    user2 = await client.fetch_user(user2_id)
    username1 = await get_username_from_id(user1_id)
    embedd = discord.Embed(colour=0x0070FF ,title=f"New reaction recived   :mailbox_with_mail: " , description=  f"``{username1}`` reacted {reaction}  on your post ``{post_id}``")
    embedd.set_thumbnail(url= user1.display_avatar.url)
    await embed_ntf (user2 , embedd)

    # await user2.send(embed = embedd  , view = Seen())




async def get_user_from_post(post_id):
    try:
        cr.execute(f"select user_id from users_posts where post_id = ?" , (post_id,))
        user_id = int(cr.fetchone()[0])
        return user_id
    except:
        return None

async def get_username_from_id(user_id) :
    try:
        cr.execute(f"select username from registers_users where user_id = '{user_id}'")
        username = cr.fetchone()[0] 
        return username
    except:
        return None


async def get_rule_from_id(user_id):
    try:
        cr.execute(f"select rank from registers_users where user_id = '{user_id}' ")
        rank = cr.fetchone()[0] 
        return rank
    except:
        return None



async def get_lang_from_id(user_id):
    try:
        cr.execute("select lang from registers_users where user_id = ? " , (user_id,))
        lang = cr.fetchone()[0]
        return lang
    except:
        return None



async def set_lang_from_id(user_id , lang):
    cr.execute("update registers_users set lang = ? where user_id = ? " , (lang,user_id,))
    db.commit()


async def of_ntf(user_id , fun):
    if fun == "on":
        cr.execute("update registers_users set ntf = ? where user_id = ?" , ("on",user_id,))

    elif fun == "off":
        cr.execute("update registers_users set ntf = ? where user_id = ?" , ("off",user_id,))

    db.commit()


async def check_ntf(user_id):
    cr.execute("select ntf from registers_users where user_id = ?" ,  (user_id,))
    check = cr.fetchone()[0]
    if "on" in check:
        return True
    elif "off" in check:
        return False



async def ar_ntf(user_id , ntf , fun):
    if fun == "A":
        cr.execute("update registers_users set ntfs =(ntfs || ? )where user_id = ? " , ("\n" + ntf , user_id,))
        db.commit()
    elif fun == "R":
        cr.execute("update registers_users set ntfs =replace(ntfs , ? ,'') where user_id = ? " , ("\n" + ntf , user_id,))
        db.commit()




async def embed_ntf(user , ntf):
    check = await check_ntf(user.id)
    if check  == True:
        await user.send(embed = ntf , view = Seen())    
    elif check == False:
        ntf = ntf.to_dict()
        ntf = json.dumps(ntf)
        await ar_ntf(user.id , ntf , "A")    




async def log(what , message ,who , log = 1 ,fun = 1 ):
    if fun == 1:
        embedd = discord.Embed(colour=0x0070FF ,title=f"{what}" , description=  f"")
        embedd.add_field(name="User: " ,value=f"{who.mention}", inline= False)
        embedd.add_field(name="Message" ,value=f"{message}", inline= False)
        embedd.set_thumbnail(url= who.display_avatar.url)
        embedd.set_footer(text = footer())
        guild =await client.fetch_guild(main_guild)

    elif fun == 2:
        embedd = discord.Embed(colour=0x0070FF ,title=f"{what}" , description=  f"")
        embedd.add_field(name="Message" ,value=f"{message}", inline= False)
        embedd.set_footer(text = footer())
        guild =await client.fetch_guild(main_guild)

    if log == 1:
        log_channel = await guild.fetch_channel(log_room)
        await log_channel.send(embed = embedd)
    elif log == 2:
        log_channel = await guild.fetch_channel(log_room2)
        await log_channel.send(embed = embedd)        






@client.tree.command(name="watch",description="watch command")
@app_commands.guild_only()
@app_commands.check(is_have_account2)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
async def watch(interaction:discord.interactions ):
    user = interaction.user
    channel = interaction.channel
    vieww = Watch_select(channel,user)
    watch_message = await interaction.channel.send(view =vieww )
    await interaction.response.send_message("**=======================**")
    await interaction.delete_original_response()
    await check_watch_before(user_id= user.id)
    cr.execute(f"update registers_users set watch_message = '{watch_message.guild.id},{watch_message.channel.id},{watch_message.id}' where user_id = '{user.id}' ")
    db.commit()        





@client.tree.command(name="notification",description="notifications command")
@app_commands.guild_only()
@app_commands.check(is_have_account2)
@app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
async def notification(interaction:discord.interactions , on_off:str ):
    user_id = interaction.user.id
    if on_off.lower() == "on":
        await of_ntf(user_id= user_id , fun= "on")
        await interaction.response.send_message("**you have been turn on your notification🟢**",ephemeral = True)
    elif on_off.lower() == "off":
        await of_ntf(user_id= user_id , fun= "off")
        await interaction.response.send_message("**you have been turn off your notification🔴**",ephemeral = True)

    else:
        await interaction.response.send_message("**please choose on or off 🙄**",ephemeral = True)
        




def get_bluoz(user_id):
    cr.execute("select bluoz from registers_users where user_id = ?", (user_id,))
    bluoz = cr.fetchone()[0]
    return bluoz


@client.tree.command(name="bluoz",description="bluoz command")
@app_commands.guild_only()
@app_commands.check(is_have_account2)
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def bluoz(interaction:discord.interactions ):
    user_id = interaction.user.id
    bluoz = get_bluoz(user_id)
    await interaction.response.send_message(f"**{interaction.user.name}, you have  ``{bluoz}``  bluoz in your account**")







@client.tree.command(name="view_post",description="view_post command")
@app_commands.guild_only()
@app_commands.check(is_have_account2)
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def view_post(interaction:discord.interactions ,post_id:int):
    if post_id == 0:
        return "eror"
    cr.execute("select user_id from users_posts where post_id = ?" , (post_id,))
    check = cr.fetchone()
    if check != None:
        embedd = await post_with_id(post_id , "V")
        await interaction.response.send_message(embed = embedd)



async def get_all_views(user_id , posts = None):
    views_num = 0
    if posts == None:
        cr.execute("select post_id from users_posts where user_id = ? order by activity desc " , (user_id,))
        posts = cr.fetchall()        
    if posts != None:
        for post in posts:
            post_id =post[0] 
            cr.execute("select views from users_posts where post_id = ? " , (post_id,))
            views = cr.fetchone()[0]
            views_post_num = (len(views.replace("\r" , "").split("\n"))) - 1
            views_num += views_post_num

    return views_num

async def get_all_reactions(user_id , posts = None):
    activity_num = 0
    if posts == None:
        cr.execute("select post_id from users_posts where user_id = ? order by activity desc " , (user_id,))
        posts = cr.fetchall()            
    if posts != None:
        for post in posts:
            post_id =post[0] 
            cr.execute("select activity from users_posts where post_id = ? " , (post_id,))
            activity = cr.fetchone()[0]
            activity_num += activity

    return activity_num

async def profilee(user_id , user):
    followers =await get_followers(user_id,fun= "num")
    following =await get_following(user_id,fun= "num")
    reactions = 0
    bluoz = get_bluoz(user_id)
    username = await get_username_from_id(user_id)
    rank =await get_rule_from_id(user_id)
    views = 0
    cr.execute("select post_id from users_posts where user_id = ? order by activity desc " , (user_id,))
    posts = cr.fetchall()
    if posts == []:
        posts_num = 0
        top_post = "None"
        reactions = 0
        views = 0
    else:
        posts_num = len(posts)
        top_post = posts[0][0]
        views =await get_all_views(user_id , posts=posts)
        reactions =await get_all_reactions(user_id , posts= posts)

    embedd = discord.Embed(colour=0x0070FF ,title=f"|{rank}|: ``{username}`` Profile" , description=  f"**Bluoz :** ``{bluoz}``")
    embedd.add_field(name="Posts 🖼:" , value=f"{posts_num}" , inline=True)
    embedd.add_field(name="Followers 🚻:" , value=f"{followers}" , inline=True)
    embedd.add_field(name="Following 🚹:" , value=f"{following}" , inline=True)


    embedd.add_field(name="Top Post 🔝:" , value=f"``{top_post}``" , inline=True)
    embedd.add_field(name="Total Views ✨:" , value=f"{views}" , inline=True)
    embedd.add_field(name="Total Reactions 🎃:" , value=f"{reactions}" , inline=True)
    embedd.set_thumbnail(url=f"{user.display_avatar.url}")
    embedd.set_footer(text=footer())
    return embedd


@client.tree.command(name="profile",description="profile command")
@app_commands.guild_only()
@app_commands.check(is_have_account2)
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def profile(interaction:discord.interactions):
    user = interaction.user
    user_id = interaction.user.id
    embedd = await profilee(user_id , user)
    await interaction.response.send_message(f"{user.mention}",embed = embedd)


async def post_profile(post_id , user):
    user_id = user.id
    like_reactions = await hm_reactions(post_id , "like")
    sad_reactions = await hm_reactions(post_id , "sad")
    haha_reactions = await hm_reactions(post_id , "haha")
    actv = (like_reactions + sad_reactions + haha_reactions )
    views = await get_views(post_id)
    if views != 0 :
        actvyy = (actv/views ) * 100
    else:
        actvyy = 0

    username = await get_username_from_id(user_id)
    rank =await get_rule_from_id(user_id)
    cr.execute("select description ,photo from users_posts where post_id = ?" , (post_id,))
    data = cr.fetchone()
    description = data[0]
    photo = data[1]
    embedd = discord.Embed(colour=0x0070FF ,title=f"**Post ID :** ``{post_id}`` stats" , description=  f"")
    embedd.add_field(name="likes ❤:" , value=f"{like_reactions}" , inline=True)
    embedd.add_field(name="haha 😂" , value=f"{haha_reactions}" , inline=True)
    embedd.add_field(name="sad 😢:" , value=f"{sad_reactions}" , inline=True)


    embedd.add_field(name="Activity rate :" , value=f"``{int(actvyy)} %``" , inline=True)
    embedd.add_field(name="Total Views ✨:" , value=f"{views}" , inline=True)

    embedd.add_field(name=f"{rank}   :man_raising_hand:   :" , value=f"``{username}``" , inline=False)
    embedd.add_field(name="description   :page_facing_up:  :" , value=f"``{description}``" , inline=False)
    embedd.set_image(url= photo)

    embedd.set_thumbnail(url=f"{user.display_avatar.url}")
    embedd.set_footer(text=footer())
    return embedd


@client.tree.command(name="post_stats",description="post_stats command")
@app_commands.guild_only()
@app_commands.check(is_have_account2)
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def post_stats(interaction:discord.interactions , post_id:int):
    post_user_id = await get_user_from_post(post_id)
    if interaction.user.id == post_user_id:
        user = interaction.user
        embedd = await post_profile(post_id , user)
        await interaction.response.send_message(f"{user.mention}",embed = embedd)

    else:
        await interaction.response.send_message("**This Not Your Post**" ,ephemeral = True )







async def top_bluozz(num = 10 , fun = "list"):
    cr.execute('select username , bluoz from registers_users order by bluoz desc')
    top_list = cr.fetchmany(num)    
    if fun == "list":
        return top_list
    elif fun == "embed":
        top_message = ""
        for user in top_list: 
            line = f"``#{(top_list.index(user)) + 1}`` **- {user[0]}   -=>  ** ``{user[1]}`` \n"
            top_message += line

        embedd = discord.Embed(colour=0x0070FF ,title=f"**Top Bluoz 💫:**" , description=  f"{top_message}")
        embedd.set_footer(text=footer())
        return embedd

@client.tree.command(name="top_bluoz",description="top_bluoz command")
@app_commands.guild_only()
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def top_bluoz(interaction:discord.interactions ):
    embedd = await top_bluozz(num= 10 , fun = "embed")
    await interaction.response.send_message(embed = embedd)




async def top_postss(num = 10 , fun = "list"):
    cr.execute('select user_id , post_id from users_posts order by activity desc')
    top_list = cr.fetchmany(num)    
    if fun == "list":
        return top_list
    elif fun == "embed":
        top_message = ""
        for post in top_list: 
            username = await get_username_from_id(post[0])
            line = f"``#{(top_list.index(post)) + 1}`` **- {username}   -=>  ** ``{post[1]}`` \n"
            top_message += line

        embedd = discord.Embed(colour=0x0070FF ,title=f"**Top posts 🖼:**" , description=  f"{top_message}")
        embedd.set_footer(text=footer())
        return embedd

@client.tree.command(name="top_posts",description="top_posts command")
@app_commands.guild_only()
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def top_posts(interaction:discord.interactions ):
    embedd = await top_postss(num= 10 , fun = "embed")
    await interaction.response.send_message(embed = embedd)





async def top_followerss(num = 10 , fun = "list"):
    cr.execute('select username ,user_id from registers_users order by length(followers) desc')
    top_list = cr.fetchmany(num)    
    if fun == "list":
        return top_list
    elif fun == "embed":
        top_message = ""
        for user in top_list: 
            followers = await get_followers(user[1] ,fun="num")
            line = f"``#{(top_list.index(user)) + 1}`` **- {user[0]}   -=>  ** ``{followers}`` \n"
            top_message += line

        embedd = discord.Embed(colour=0x0070FF ,title=f"**Top user followers 🚻:**" , description=  f"{top_message}")
        embedd.set_footer(text=footer())
        return embedd


@client.tree.command(name="top_followers",description="top_followers command")
@app_commands.guild_only()
@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
async def top_followers(interaction:discord.interactions ):
    embedd = await top_followerss(num= 10 , fun = "embed")
    await interaction.response.send_message(embed = embedd)




# -----------------------------{Events -=> System}-----------------------------




@client.event
async def on_member_remove(member):
    # -------------------{part of -=> Register-Login -=> System}-----------------
    await check2(member)








# ========{Eror Bypass}==================================

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        pass
    elif isinstance(error, MissingPermissions):
        pass

    elif isinstance(error , MemberNotFound):
        pass



@tree.error
async def on_app_command_error(interaction:discord.Interaction , error):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f'**``{interaction.user.name}``** ,Cool down (**{round(error.retry_after, 2)} seconds left **)' , ephemeral= True)



@client.event
async def on_ready():
    print("WE ARE READY")
    try:
        synced = await client.tree.sync()
        print(f"Synceed {len(synced)} command(s)")
    except Exception as e:
        print(e)


@client.event
async def on_message(message):
    if message.channel.id == post_room_ar:
        await check_post(message.author,message , "ar")
    elif message.channel.id == post_room_en:
        await check_post(message.author,message , "en")


    await client.process_commands(message)


@client.event
async def on_guild_join(guild):
    message = f"``{guild.name}`` **added our bot 😊**"
    what = "``Social Media`` ** has been Join new server 🎉**"
    await log(what , message , guild , fun=2 , log=2)


@client.event
async def on_guild_remove(guild):
    message = f"``{guild.name}`` **removed our bot 🙄**"
    what = "``Social Media`` ** has been leave new server 😔**"
    await log(what , message , guild , fun=2 , log=2)


client.run(Token)
