"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from evennia.contrib.rpg.character_creator.character_creator import ContribChargenCmdSet

from commands.cthulhu import (
    CmdScore, CmdTrain, CmdPractice, CmdLearn, CmdDebate, CmdProf,
    CmdConsider, CmdKill, CmdFlee, CmdWimpy, CmdSay, CmdCast,
    CmdHome, CmdLook, CmdInventory, CmdGet, CmdDrop, CmdGive,
    CmdSetDesc, CmdWhisper, CmdPose, CmdWho, CmdQuit, CmdAccess,
    CmdExperience, CmdResearch, CmdDuel, CmdRighteouskill,
    CmdRitual, CmdSpell, CmdSpells, CmdSkills, CmdSkill, CmdAbout,
)
from commands.cthulhu_help import CmdHelp, CmdSetHelp
from commands.cthulhu_comms import CmdPage
from commands.cthulhu_building import (
    CmdCreate, CmdDesc, CmdDestroy, CmdDig, CmdTunnel,
    CmdLink, CmdUnLink, CmdSetHome, CmdName, CmdOpen,
)
from commands.cthulhu_building_advanced import (
    CmdSetObjAlias, CmdCopy, CmdCpAttr, CmdMvAttr, CmdSetAttribute,
    CmdTypeclass, CmdWipe, CmdLock, CmdExamine, CmdFind,
    CmdScripts, CmdObjects, CmdTeleport, CmdTag, CmdSpawn,
)
from commands.cthulhu_nick import CmdNick
from commands.cthulhu_account import (
    CmdOOCLook, CmdCharCreate, CmdCharDelete, CmdIC, CmdOOC,
    CmdSessions, CmdOption, CmdPassword, CmdColorTest, CmdQuell, CmdStyle,
)
from commands.cthulhu_unloggedin import (
    CmdUnconnectedConnect, CmdUnconnectedCreate, CmdUnconnectedQuit,
    CmdUnconnectedLook, CmdUnconnectedHelp, CmdUnconnectedEncoding,
    CmdUnconnectedScreenreader, CmdUnconnectedInfo, CmdUnconnectedChat,
)
from commands.cthulhu_admin import (
    CmdBoot, CmdBan, CmdUnban, CmdEmit, CmdNewPassword,
    CmdPerm, CmdWall, CmdForce,
)
from commands.cthulhu_channels import CmdChannel
from commands.cthulhu_dream import CmdDream, CmdWake
from commands.cthulhu_shop import CmdList, CmdBuy, CmdSell
from commands.cthulhu_bank import CmdDeposit, CmdWithdraw, CmdBalance, CmdExchange
from commands.cthulhu_money import CmdMoney
from commands.cthulhu_inn import CmdAlloggia
from commands.cthulhu_equip import (
    CmdWear, CmdWield, CmdRemove, CmdEquipment,
)
from commands.cthulhu_forgiatura import CmdForge, CmdFix, CmdRefit, CmdGunsmith, CmdReload
from commands.cthulhu_locker import CmdLocker
from commands.cthulhu_sopravvivenza import CmdEat, CmdDrink, CmdFeed, CmdFeedMe
from commands.cthulhu_sanita import CmdTherapy, CmdPsychology
from commands.cthulhu_clan import CmdClan
from commands.cthulhu_sottorazze import (
    CmdSubrace, CmdLineage, CmdLich, CmdVampire, CmdWere, CmdBite, CmdPrivacy,
)
from commands.cthulhu_yithian import CmdMindtransfer, CmdReturn, CmdYithAdapt, CmdYithAbduct
from commands.cthulhu_pk import (
    CmdMurder, CmdBounty, CmdMission, CmdDeliver,
    CmdAutogold, CmdAutoloot, CmdAutokill, CmdNoloot, CmdAutolist, CmdAutosac,
)
from commands.cthulhu_worship import CmdWorship, CmdSacrifice
from commands.cthulhu_socials import COMANDI_SOCIAL, CmdGender
from commands.cthulhu_scenografia import CmdED
from commands.cthulhu_imprese import CmdDeed, CmdQuest
from commands.cthulhu_focus_crystal import CmdLore, CmdUse
from commands.cthulhu_canali import (
    CmdGossip, CmdInvestigatorTalk, CmdHero, CmdRemTalk, CmdImmTalk,
    CmdQuestion, CmdMusic, CmdChannels, CmdQuiet, CmdReply, CmdIgnore,
    CmdChat,
)
from commands.cthulhu_affects import CmdAffects, CmdRaffects
from commands.cthulhu_porte import CmdOpenPorta, CmdClosePorta, CmdLockPorta, CmdUnlockPorta, CmdPick
from commands.cthulhu_remort import CmdRemort
from commands.cthulhu_seguaci import CmdTame, CmdOrder
from commands.cthulhu_voodoo import CmdCut, CmdVoodoo
from commands.cthulhu_gruppo import (
    CmdFollow, CmdNofollow, CmdGroup, CmdGtell, CmdSplit, CmdAutosplit, CmdAutoassist,
)
from commands.cthulhu_posizione import CmdRest, CmdSleep, CmdStand
from commands.cthulhu_tempo import CmdTime, CmdHours
from commands.cthulhu_illuminazione import CmdLight, CmdExtinguish
from commands.cthulhu_mosse_speciali import (
    CmdKick, CmdBash, CmdTrip, CmdDisarm, CmdDirtKicking, CmdBackstab,
)
from commands.cthulhu_prontuario import CmdComandi
from commands.cthulhu_staff import (
    CmdHolylight, CmdRestore, CmdAdvance, CmdSlay, CmdFreeze, CmdPeace,
    CmdWizinvis, CmdCloak, CmdWizlock, CmdNewlock, CmdSwitch, CmdIncarnate,
    CmdGoto, CmdBamfin, CmdBamfout, CmdPermapk, CmdCostruisciMondo,
)


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdAbout)
        self.add(CmdScore)
        self.add(CmdExperience)
        self.add(CmdRighteouskill)
        self.add(CmdResearch)
        self.add(CmdTrain)
        self.add(CmdPractice)
        self.add(CmdLearn)
        self.add(CmdDebate)
        self.add(CmdProf)
        self.add(CmdConsider)
        self.add(CmdKill)
        self.add(CmdFlee)
        self.add(CmdWimpy)
        self.add(CmdSay)
        self.add(CmdCast)
        self.add(CmdRitual)
        self.add(CmdSpell)
        self.add(CmdSpells)
        self.add(CmdSkills)
        self.add(CmdSkill)
        self.add(CmdDuel)
        self.add(CmdHome)
        self.add(CmdLook)
        self.add(CmdInventory)
        self.add(CmdGet)
        self.add(CmdDrop)
        self.add(CmdGive)
        self.add(CmdSetDesc)
        self.add(CmdWhisper)
        self.add(CmdPose)
        self.add(CmdHelp)
        self.add(CmdSetHelp)
        self.add(CmdCreate)
        self.add(CmdDesc)
        self.add(CmdDestroy)
        self.add(CmdDig)
        self.add(CmdTunnel)
        self.add(CmdLink)
        self.add(CmdUnLink)
        self.add(CmdSetHome)
        self.add(CmdName)
        self.add(CmdOpen)
        self.add(CmdSetObjAlias)
        self.add(CmdCopy)
        self.add(CmdCpAttr)
        self.add(CmdMvAttr)
        self.add(CmdSetAttribute)
        self.add(CmdTypeclass)
        self.add(CmdWipe)
        self.add(CmdLock)
        self.add(CmdExamine)
        self.add(CmdFind)
        self.add(CmdScripts)
        self.add(CmdObjects)
        self.add(CmdTeleport)
        self.add(CmdTag)
        self.add(CmdSpawn)
        self.add(CmdNick)
        self.add(CmdAccess)
        self.add(CmdDream)
        self.add(CmdWake)
        self.add(CmdList)
        self.add(CmdBuy)
        self.add(CmdSell)
        self.add(CmdTime)
        self.add(CmdHours)
        self.add(CmdLight)
        self.add(CmdExtinguish)
        self.add(CmdKick)
        self.add(CmdBash)
        self.add(CmdTrip)
        self.add(CmdDisarm)
        self.add(CmdDirtKicking)
        self.add(CmdBackstab)
        self.add(CmdHolylight)
        self.add(CmdRestore)
        self.add(CmdAdvance)
        self.add(CmdSlay)
        self.add(CmdFreeze)
        self.add(CmdPeace)
        self.add(CmdWizinvis)
        self.add(CmdCloak)
        self.add(CmdWizlock)
        self.add(CmdNewlock)
        self.add(CmdSwitch)
        self.add(CmdIncarnate)
        self.add(CmdGoto)
        self.add(CmdBamfin)
        self.add(CmdBamfout)
        self.add(CmdPermapk)
        self.add(CmdCostruisciMondo)
        self.add(CmdDeposit)
        self.add(CmdWithdraw)
        self.add(CmdBalance)
        self.add(CmdExchange)
        self.add(CmdMoney)
        self.add(CmdAlloggia)
        self.add(CmdRest)
        self.add(CmdSleep)
        self.add(CmdStand)
        self.add(CmdWear)
        self.add(CmdWield)
        self.add(CmdRemove)
        self.add(CmdEquipment)
        self.add(CmdForge)
        self.add(CmdFix)
        self.add(CmdRefit)
        self.add(CmdGunsmith)
        self.add(CmdReload)
        self.add(CmdLocker)
        self.add(CmdEat)
        self.add(CmdDrink)
        self.add(CmdFeed)
        self.add(CmdFeedMe)
        self.add(CmdTherapy)
        self.add(CmdPsychology)
        self.add(CmdClan)
        self.add(CmdSubrace)
        self.add(CmdLineage)
        self.add(CmdLich)
        self.add(CmdVampire)
        self.add(CmdWere)
        self.add(CmdBite)
        self.add(CmdPrivacy)
        self.add(CmdMindtransfer)
        self.add(CmdReturn)
        self.add(CmdYithAdapt)
        self.add(CmdYithAbduct)
        self.add(CmdMurder)
        self.add(CmdBounty)
        self.add(CmdMission)
        self.add(CmdDeliver)
        self.add(CmdAutogold)
        self.add(CmdAutoloot)
        self.add(CmdAutokill)
        self.add(CmdNoloot)
        self.add(CmdAutolist)
        self.add(CmdAutosac)
        self.add(CmdWorship)
        self.add(CmdSacrifice)
        self.add(CmdGender)
        for comando_social in COMANDI_SOCIAL:
            self.add(comando_social)
        self.add(CmdED)
        self.add(CmdDeed)
        self.add(CmdQuest)
        self.add(CmdLore)
        self.add(CmdUse)
        self.add(CmdGossip)
        self.add(CmdInvestigatorTalk)
        self.add(CmdHero)
        self.add(CmdRemTalk)
        self.add(CmdImmTalk)
        self.add(CmdQuestion)
        self.add(CmdMusic)
        self.add(CmdChannels)
        self.add(CmdQuiet)
        self.add(CmdReply)
        self.add(CmdIgnore)
        self.add(CmdChat)
        self.add(CmdAffects)
        self.add(CmdRaffects)
        self.add(CmdOpenPorta)
        self.add(CmdClosePorta)
        self.add(CmdLockPorta)
        self.add(CmdUnlockPorta)
        self.add(CmdPick)
        self.add(CmdRemort)
        self.add(CmdTame)
        self.add(CmdOrder)
        self.add(CmdCut)
        self.add(CmdVoodoo)
        self.add(CmdFollow)
        self.add(CmdNofollow)
        self.add(CmdGroup)
        self.add(CmdGtell)
        self.add(CmdSplit)
        self.add(CmdAutosplit)
        self.add(CmdAutoassist)
        self.add(CmdBoot)
        self.add(CmdBan)
        self.add(CmdUnban)
        self.add(CmdEmit)
        self.add(CmdNewPassword)
        self.add(CmdPerm)
        self.add(CmdWall)
        self.add(CmdForce)
        self.add(CmdComandi)

        # Nomi italiani dei comandi (world/comandi_italiano.py). Va per
        # ultimo, quando tutti i comandi sono stati aggiunti: la funzione
        # scorre il cmdset e aggiunge a ciascuno i propri alias. I nomi
        # inglesi restano validi - un alias si affianca, non sostituisce.
        from world.comandi_italiano import applica_alias_italiani
        applica_alias_italiani(self)


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(ContribChargenCmdSet)  # CmdCharCreate("charcreate") -> world/chargen_menu.py (CHARGEN_MENU)
        self.add(CmdWho)
        self.add(CmdQuit)
        self.add(CmdPage)
        self.add(CmdOOCLook)
        self.add(CmdCharCreate)  # sottoclasse di ContribCmdCharCreate con NEWLOCK - vedi commands/cthulhu_account.py
        self.add(CmdCharDelete)
        self.add(CmdIC)
        self.add(CmdOOC)
        self.add(CmdSessions)
        self.add(CmdOption)
        self.add(CmdPassword)
        self.add(CmdColorTest)
        self.add(CmdQuell)
        self.add(CmdStyle)
        self.add(CmdChannel)


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(CmdUnconnectedConnect)
        self.add(CmdUnconnectedCreate)
        self.add(CmdUnconnectedQuit)
        self.add(CmdUnconnectedLook)
        self.add(CmdUnconnectedHelp)
        self.add(CmdUnconnectedEncoding)
        self.add(CmdUnconnectedScreenreader)
        self.add(CmdUnconnectedInfo)
        self.add(CmdUnconnectedChat)


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
