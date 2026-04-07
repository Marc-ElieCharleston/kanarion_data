"""Add dialogue_give and dialogue_complete to all side + repeatable quests."""
import json

with open('world/quests.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

dialogues = {
    # === ZONE 01 ===
    "q_side_farmer_betes": {
        "dialogue_give_fr": "Mes champs sont envahis. Des rats et des scarabees partout. Ca fait deux semaines que je dors pas. Si tu peux en eliminer quelques uns je te paierai ce que je peux.",
        "dialogue_give_en": "My fields are overrun. Rats and scarabs everywhere. I haven't slept in two weeks. If you can take out a few I'll pay what I can.",
        "dialogue_complete_fr": "Tu les as eus ? Merci. Je vais enfin pouvoir dormir tranquille. Tiens c'est pas grand chose mais tu l'as merite.",
        "dialogue_complete_en": "You got them? Thanks. I can finally sleep in peace. Here it's not much but you earned it."
    },
    "q_side_star_hunter": {
        "dialogue_give_fr": "Y a un groupe de betes plus coriaces que les autres dans les plaines. Deux etoiles au moins. Si t'es assez costaud pour t'en occuper j'ai une prime pour toi.",
        "dialogue_give_en": "There's a pack of beasts tougher than the rest in the plains. Two stars at least. If you're tough enough to handle them I've got a bounty for you.",
        "dialogue_complete_fr": "Pas mal. T'es plus solide que t'en as l'air. Reviens me voir si tu veux du defi.",
        "dialogue_complete_en": "Not bad. You're tougher than you look. Come back if you want a real challenge."
    },
    "q_rep_plaines": {
        "dialogue_give_fr": "Les plaines ont encore besoin d'etre nettoyees. Rats et scarabees ca n'arrete jamais. Si t'as rien de mieux a faire va en eliminer quelques uns.",
        "dialogue_give_en": "The plains still need clearing. Rats and scarabs it never stops. If you've got nothing better to do go take out a few.",
        "dialogue_complete_fr": "Bon travail. Ca reviendra mais au moins les routes sont calmes pour un moment.",
        "dialogue_complete_en": "Good work. They'll be back but at least the roads are quiet for now."
    },
    # === ZONE 02 ===
    "q_side_foret": {
        "dialogue_give_fr": "Les betes de la lisiere sont nerveuses. Des loups qui s'approchent du village des sangliers qui chargent les voyageurs. Faut securiser la zone avant que quelqu'un se fasse blesser.",
        "dialogue_give_en": "The beasts at the forest edge are nervous. Wolves approaching the village boars charging travelers. We need to secure the area before someone gets hurt.",
        "dialogue_complete_fr": "C'est plus calme. Merci. Mais garde un oeil ouvert la prochaine fois que tu passes par la.",
        "dialogue_complete_en": "It's calmer now. Thanks. But keep an eye out next time you pass through."
    },
    "q_side_boar_hunt": {
        "dialogue_give_fr": "Un sanglier alpha terrorise la route de la foret. Les voyageurs font des detours de deux heures pour l'eviter. Grosse bete mauvais caractere. Si tu l'abats la prime est pour toi.",
        "dialogue_give_en": "An alpha boar is terrorizing the forest road. Travelers take two hour detours to avoid it. Big beast bad temper. Take it down and the bounty is yours.",
        "dialogue_complete_fr": "Le sanglier alpha. Impressionnant. Voila ta prime.",
        "dialogue_complete_en": "The alpha boar. Impressive. Here's your bounty."
    },
    "q_side_elara_chariot": {
        "dialogue_give_fr": "Mon fils est parti avec le chariot vers le sud il y a trois jours. Il devait revenir le lendemain. J'ai peur qu'il lui soit arrive quelque chose. Si tu pouvais chercher le chariot dans la foret...",
        "dialogue_give_en": "My son left with the cart heading south three days ago. He was supposed to be back the next day. I'm afraid something happened to him. If you could look for the cart in the forest...",
        "dialogue_complete_fr": "Tu l'as trouve ? Et mon fils... il va bien ?",
        "dialogue_complete_en": "You found it? And my son... is he okay?"
    },
    "q_rep_foret": {
        "dialogue_give_fr": "La lisiere a encore besoin d'attention. Les loups et les sangliers reviennent des que le calme s'installe.",
        "dialogue_give_en": "The forest edge needs attention again. Wolves and boars come back as soon as things settle down.",
        "dialogue_complete_fr": "Bien. Ca tient pour le moment.",
        "dialogue_complete_en": "Good. It holds for now."
    },
    # === ZONE 03 ===
    "q_side_dorian_loups": {
        "dialogue_give_fr": "Encore trois brebis cette nuit. Les loups descendent des collines et les beliers sauvages defoncent les clotures. A ce rythme il me restera rien d'ici la fin du mois. Tu peux m'aider ?",
        "dialogue_give_en": "Three more sheep last night. Wolves come down from the hills and wild rams break through the fences. At this rate I'll have nothing left by the end of the month. Can you help?",
        "dialogue_complete_fr": "Mes betes sont un peu plus tranquilles ce matin. C'est deja ca. Merci l'ami.",
        "dialogue_complete_en": "My animals are a bit calmer this morning. That's something. Thanks friend."
    },
    "q_rep_collines": {
        "dialogue_give_fr": "Les collines restent infestees. Chaque patrouille compte. T'es disponible ?",
        "dialogue_give_en": "The hills are still infested. Every patrol counts. You available?",
        "dialogue_complete_fr": "Rapport note. Bonne patrouille.",
        "dialogue_complete_en": "Report noted. Good patrol."
    },
    "q_rep_elite_hunt": {
        "dialogue_give_fr": "J'ai repere une bete plus grosse que les autres dans les collines. Ca t'interesse ?",
        "dialogue_give_en": "I spotted a beast bigger than the others in the hills. Interested?",
        "dialogue_complete_fr": "Elite abattu prime payee. Comme d'habitude.",
        "dialogue_complete_en": "Elite down bounty paid. As usual."
    },
    # === ZONE 04 ===
    "q_side_bandits_route": {
        "dialogue_give_fr": "Les bandits profitent du chaos. Ils pillent les convois entre Kanarion et le sud. Leur camp est dans les gorges. Affaiblis les. On a pas les hommes pour une attaque frontale mais si tu reduis leurs effectifs ca nous aidera.",
        "dialogue_give_en": "Bandits are taking advantage of the chaos. They're raiding convoys between Kanarion and the south. Their camp is in the gorges. Weaken them. We don't have the men for a frontal assault but if you thin their numbers it'll help.",
        "dialogue_complete_fr": "Bien joue. Ils vont y reflechir a deux fois avant de s'attaquer aux convois. Du moins pour un temps.",
        "dialogue_complete_en": "Well done. They'll think twice before hitting convoys. At least for a while."
    },
    "q_side_bandit_chief": {
        "dialogue_give_fr": "Le chef des bandits. Tant qu'il est la ils se regroupent. Elimine le et le camp s'effondre. Prime elevee pour celui la.",
        "dialogue_give_en": "The bandit chief. As long as he's there they regroup. Take him out and the camp falls apart. High bounty for this one.",
        "dialogue_complete_fr": "Le chef est tombe ? Parfait. Sans lui les autres vont se disperser. Bien merite.",
        "dialogue_complete_en": "The chief is down? Perfect. Without him the rest will scatter. Well earned."
    },
    "q_side_gaspard_route": {
        "dialogue_give_fr": "Il existe un vieux chemin qui contourne le camp des bandits. J'y passais quand j'etais jeune. Mais des pillards s'y sont installes. Si tu degages le passage je te montrerai le raccourci.",
        "dialogue_give_en": "There's an old path that goes around the bandit camp. I used to take it when I was young. But raiders have set up there. Clear the way and I'll show you the shortcut.",
        "dialogue_complete_fr": "Le chemin est libre ? Bien. Passe par le rocher en forme de crane tourne a gauche et longe la riviere. C'est plus rapide et plus discret.",
        "dialogue_complete_en": "The path is clear? Good. Go past the skull shaped rock turn left and follow the river. It's faster and more discreet."
    },
    "q_side_bandit_reddition": {
        "dialogue_give_fr": "On a localise un groupe de bandits dans le repaire. Nettoie la zone. Mais fais attention certains sont peut etre prets a se rendre. A toi de voir comment tu geres ca.",
        "dialogue_give_en": "We've located a group of bandits in the hideout. Clean the area. But be careful some might be ready to surrender. Up to you how you handle it.",
        "dialogue_complete_fr": "C'est fait. Et le prisonnier... je te laisse decider.",
        "dialogue_complete_en": "It's done. And the prisoner... I'll let you decide."
    },
    "q_rep_bandits": {
        "dialogue_give_fr": "Les bandits reviennent toujours. Tant qu'il y a du profit ils tenteront leur chance. Une patrouille de plus ca aide.",
        "dialogue_give_en": "Bandits always come back. As long as there's profit they'll try their luck. One more patrol helps.",
        "dialogue_complete_fr": "Les routes sont un peu plus sures. Pour le moment.",
        "dialogue_complete_en": "The roads are a bit safer. For now."
    },
    # === ZONE 05 ===
    "q_side_plaines_sauvages": {
        "dialogue_give_fr": "J'ai repere des marques plus profondes dans les plaines sauvages. Le probleme c'est les hyenes. Elles sont partout et elles attaquent a vue. Si tu pouvais en eliminer assez pour que je puisse aller examiner les marques...",
        "dialogue_give_en": "I spotted deeper marks in the wild plains. Problem is the hyenas. They're everywhere and they attack on sight. If you could take out enough for me to go examine the marks...",
        "dialogue_complete_fr": "Merci. J'ai pu approcher les marques. C'est... preoccupant. Elles sont plus anciennes que je pensais. Mais ca c'est mon probleme. Tiens pour ta peine.",
        "dialogue_complete_en": "Thanks. I was able to reach the marks. It's... concerning. They're older than I thought. But that's my problem. Here for your trouble."
    },
    "q_rep_plaines_sauvages": {
        "dialogue_give_fr": "Les hyenes pullulent dans les plaines sauvages. Chaque volontaire qui passe par la nous aide a garder le chemin ouvert.",
        "dialogue_give_en": "Hyenas swarm the wild plains. Every volunteer who passes through helps keep the path open.",
        "dialogue_complete_fr": "Moins de hyenes c'est moins de risques pour les voyageurs. Merci.",
        "dialogue_complete_en": "Fewer hyenas means less risk for travelers. Thanks."
    },
    # === ZONE 06 ===
    "q_side_hilda_herbes": {
        "dialogue_give_fr": "Aelina a besoin de racines jaunes pour ses remedes. On les trouve que dans les marais. Avant j'y allais seule mais les betes la bas... j'ose plus. Si tu pouvais en ramasser quelques unes je t'en serais vraiment reconnaissante.",
        "dialogue_give_en": "Aelina needs yellow roots for her remedies. They only grow in the marshes. I used to go alone but the beasts there... I don't dare anymore. If you could gather a few I'd be really grateful.",
        "dialogue_complete_fr": "Tu les as ! Oh merci. Aelina va etre contente. Ces racines font des miracles pour les blessures de Souffle.",
        "dialogue_complete_en": "You got them! Oh thank you. Aelina will be happy. These roots work wonders for Breath wounds."
    },
    "q_side_marais": {
        "dialogue_give_fr": "La route vers le sud passe par les marais et des taureaux massifs bloquent le passage. Ces betes sont enormes et tres agressives. Degage la route pour que les convois puissent passer.",
        "dialogue_give_en": "The road south goes through the marshes and massive bulls are blocking the way. These beasts are huge and very aggressive. Clear the road so convoys can get through.",
        "dialogue_complete_fr": "Les convois peuvent passer. C'etait du lourd. Tu t'en es bien sorti.",
        "dialogue_complete_en": "Convoys can get through. That was tough. You handled it well."
    },
    "q_side_taniere": {
        "dialogue_give_fr": "Au coeur des marais il y a une taniere. Et au fond de cette taniere un taureau ancestral. Les chasseurs l'appellent le Vieux. Si tu le terrasses la prime est genereuse.",
        "dialogue_give_en": "Deep in the marshes there's a den. And at the heart of that den an ancient bull. Hunters call it the Old One. Take it down and the bounty is generous.",
        "dialogue_complete_fr": "Le Vieux est tombe. Je commence a me demander si t'as des limites. Belle prise.",
        "dialogue_complete_en": "The Old One is down. I'm starting to wonder if you have limits. Nice catch."
    },
    "q_rep_marais": {
        "dialogue_give_fr": "Les taureaux reviennent dans les marais. La route doit rester ouverte.",
        "dialogue_give_en": "Bulls are back in the marshes. The road must stay open.",
        "dialogue_complete_fr": "Route degagee. Bien.",
        "dialogue_complete_en": "Road cleared. Good."
    },
    # === ZONE 07 ===
    "q_side_passage": {
        "dialogue_give_fr": "Le passage rocheux c'est la seule route vers Rochebourg. Des mercenaires et des betes s'y sont installes. Tant qu'ils sont la personne ne passe. Degage le chemin.",
        "dialogue_give_en": "The rocky passage is the only road to Rochebourg. Mercenaries and beasts have settled in. As long as they're there nobody gets through. Clear the way.",
        "dialogue_complete_fr": "Le passage est ouvert. Les premiers convois devraient arriver a Rochebourg d'ici demain. Bon travail.",
        "dialogue_complete_en": "The passage is open. First convoys should reach Rochebourg by tomorrow. Good work."
    },
    "q_side_nessa_colis": {
        "dialogue_give_fr": "Je suis coincee ici a Rochebourg. Impossible de traverser le passage avec les mercenaires. J'ai un colis urgent pour Milo le marchand a Kanarion. Ca fait deux semaines qu'il attend. Si tu pouvais le lui apporter...",
        "dialogue_give_en": "I'm stuck here in Rochebourg. Can't cross the passage with the mercenaries. I've got an urgent package for Milo the merchant in Kanarion. He's been waiting two weeks. If you could deliver it...",
        "dialogue_complete_fr": "De la part de Nessa ? Enfin ! J'attendais ces fournitures depuis une eternite. Tiens pour le derangement.",
        "dialogue_complete_en": "From Nessa? Finally! I've been waiting for these supplies forever. Here for the trouble."
    },
    "q_rep_passage": {
        "dialogue_give_fr": "Le passage a besoin d'etre nettoye regulierement. Les mercenaires reviennent des qu'on baisse la garde.",
        "dialogue_give_en": "The passage needs regular clearing. Mercenaries come back as soon as we let our guard down.",
        "dialogue_complete_fr": "Passage securise. Les convois peuvent rouler.",
        "dialogue_complete_en": "Passage secured. Convoys can roll."
    },
    # === ZONE 08 ===
    "q_side_ombre_tour": {
        "dialogue_give_fr": "Les Zelotes de la Tour patrouillent de plus en plus loin. On les voit maintenant aux portes de Rochebourg. Si on fait rien ils finiront par nous encercler. Repousse leurs patrouilles.",
        "dialogue_give_en": "The Tower Zealots are patrolling further and further out. We can see them at Rochebourg's gates now. If we do nothing they'll surround us. Push back their patrols.",
        "dialogue_complete_fr": "Ca respire un peu. Mais ils reviendront. Ils reviennent toujours.",
        "dialogue_complete_en": "We can breathe a little. But they'll be back. They always come back."
    },
    "q_side_maren_mari": {
        "dialogue_give_fr": "Mon mari Oren est parti il y a six mois. Il voulait voir la Tour de ses propres yeux. Un homme grand barbe rousse cicatrice au menton. Personne ne l'a vu revenir. Si tu vas pres de la Tour... regarde s'il est encore la bas. S'il te plait.",
        "dialogue_give_en": "My husband Oren left six months ago. He wanted to see the Tower with his own eyes. Tall man red beard scar on his chin. Nobody saw him come back. If you go near the Tower... look for him. Please.",
        "dialogue_complete_fr": "Tu l'as vu ? Il est... converti ? Non. Non ca peut pas etre lui. Il disait qu'il allait juste regarder. Juste regarder...",
        "dialogue_complete_en": "You saw him? He's... converted? No. No it can't be him. He said he was just going to look. Just look..."
    },
    "q_side_zelote_blesse": {
        "dialogue_give_fr": "Un voyageur m'a dit qu'un Zelote blesse git au bord du chemin pres de la Tour. C'est peut etre un piege. C'est peut etre pas. Vas y et decide sur place.",
        "dialogue_give_en": "A traveler told me a wounded Zealot lies by the road near the Tower. Could be a trap. Could be not. Go there and decide for yourself.",
        "dialogue_complete_fr": "Alors ? Qu'est ce que t'as trouve ?",
        "dialogue_complete_en": "So? What did you find?"
    },
    "q_rep_tour_approches": {
        "dialogue_give_fr": "Les patrouilles de Zelotes continuent. Chaque volontaire qui les repousse nous donne du temps.",
        "dialogue_give_en": "Zealot patrols continue. Every volunteer who pushes them back buys us time.",
        "dialogue_complete_fr": "Encore un peu de repit. Merci.",
        "dialogue_complete_en": "A bit more respite. Thanks."
    },
    "q_rep_star3": {
        "dialogue_give_fr": "Un groupe dangereux rode pres de la Tour. Trois etoiles minimum. C'est pas pour les debutants. Interesse ?",
        "dialogue_give_en": "A dangerous pack roams near the Tower. Three stars minimum. Not for beginners. Interested?",
        "dialogue_complete_fr": "Trois etoiles. Proprement fait. Voila ta prime.",
        "dialogue_complete_en": "Three stars. Cleanly done. Here's your bounty."
    },
    # === ZONE 09 ===
    "q_side_kael_info": {
        "dialogue_give_fr": "Un ancien Zelote se cache chez nous. Il s'appelle Kael. Il a fui la Tour il y a quelques semaines et il dit qu'il a des informations importantes sur ce qui se passe a l'interieur. Va lui parler.",
        "dialogue_give_en": "A former Zealot is hiding here. His name is Kael. He fled the Tower a few weeks ago and says he has important information about what's happening inside. Go talk to him.",
        "dialogue_complete_fr": "Qu'est ce qu'il t'a dit ? Des rituels ? Des excavations ? C'est pire que ce qu'on pensait.",
        "dialogue_complete_en": "What did he tell you? Rituals? Excavations? It's worse than we thought."
    },
    "q_side_territoire_zelote": {
        "dialogue_give_fr": "Le territoire des Zelotes est completement verrouille. Nos eclaireurs ne passent plus. On a besoin de quelqu'un pour forcer le passage et degager les routes.",
        "dialogue_give_en": "Zealot territory is completely locked down. Our scouts can't get through. We need someone to force a path and clear the roads.",
        "dialogue_complete_fr": "Les eclaireurs ont pu avancer. On en sait un peu plus sur leurs positions maintenant. Bien joue.",
        "dialogue_complete_en": "The scouts were able to advance. We know a bit more about their positions now. Well done."
    },
    "q_side_converti_empathie": {
        "dialogue_give_fr": "Attends. Tu es de Rochebourg ? Non pas la peine de repondre. Je sais ce que tu penses de nous. Mais je suis pas un fanatique. J'etais fermier avant. J'avais une femme une fille. Et un jour la Tour m'a appele. Je sais pas comment l'expliquer. Tu veux ecouter ou pas ?",
        "dialogue_give_en": "Wait. You're from Rochebourg? No don't bother answering. I know what you think of us. But I'm not a fanatic. I was a farmer before. Had a wife a daughter. And one day the Tower called me. I can't explain it. Do you want to listen or not?",
        "dialogue_complete_fr": "",
        "dialogue_complete_en": ""
    },
    "q_rep_zelotes": {
        "dialogue_give_fr": "Les convertis gardent chaque chemin vers la Tour. Chaque percee nous aide a comprendre ce qui se passe la bas.",
        "dialogue_give_en": "The converts guard every path to the Tower. Every breakthrough helps us understand what's happening there.",
        "dialogue_complete_fr": "Un chemin de plus degage. Ca aide.",
        "dialogue_complete_en": "One more path cleared. It helps."
    },
    # === ZONE 10 ===
    "q_side_inquisitor": {
        "dialogue_give_fr": "Un chef Zelote qu'ils appellent le Grand Inquisiteur dirige les excavations. Extremement dangereux. La prime la plus elevee que j'ai jamais posee. Si tu y vas fais le pas a moitie.",
        "dialogue_give_en": "A Zealot leader they call the Grand Inquisitor runs the excavations. Extremely dangerous. The highest bounty I've ever posted. If you go don't do it halfway.",
        "dialogue_complete_fr": "Le Grand Inquisiteur est tombe. T'es... je sais meme pas quoi dire. Tiens. Tu l'as largement merite.",
        "dialogue_complete_en": "The Grand Inquisitor is down. You're... I don't even know what to say. Here. You more than earned it."
    },
    "q_rep_sanctuaire": {
        "dialogue_give_fr": "Les excavations sont gardees par les plus fanatiques d'entre eux. Chaque raid affaiblit leur emprise sur la zone.",
        "dialogue_give_en": "The excavations are guarded by the most fanatical among them. Every raid weakens their grip on the area.",
        "dialogue_complete_fr": "Moins de gardes aux excavations. Ca ouvre des possibilites.",
        "dialogue_complete_en": "Fewer guards at the excavations. That opens possibilities."
    },
    "q_rep_legendary": {
        "dialogue_give_fr": "Cinq etoiles. Le pire qu'on ait vu dans la region. Si t'as un groupe solide et que t'as envie de tester tes limites c'est pour toi. Sinon passe ton chemin.",
        "dialogue_give_en": "Five stars. The worst we've seen in the region. If you've got a solid group and want to test your limits this is for you. Otherwise move along.",
        "dialogue_complete_fr": "Cinq etoiles. Abattu. T'es une legende. Pas d'autre mot.",
        "dialogue_complete_en": "Five stars. Down. You're a legend. No other word for it."
    },
    # === ROCHEBOURG ===
    "q_side_voleur_rochebourg": {
        "dialogue_give_fr": "On a eu un vol a l'auberge de Bran. De la nourriture. Le voleur s'est enfui vers le passage rocheux. Retrouve le et ramene le. Ou pas. A toi de voir quand tu comprendras la situation.",
        "dialogue_give_en": "There was a theft at Bran's inn. Food. The thief fled toward the rocky passage. Find him and bring him back. Or not. Up to you once you understand the situation.",
        "dialogue_complete_fr": "Tu l'as trouve. Et maintenant... qu'est ce qu'on fait de lui ?",
        "dialogue_complete_en": "You found him. And now... what do we do with him?"
    },
}

# Apply dialogues
updated = 0
for quest in data["quests"]:
    qid = quest.get("id")
    if qid in dialogues:
        quest.update(dialogues[qid])
        updated += 1

# Convert q_side_elara_chariot to moral choice
for quest in data["quests"]:
    if quest["id"] == "q_side_elara_chariot":
        quest["moral_choice"] = {
            "moment": "on_completion",
            "description_fr": "Tu trouves le chariot renverse et le fils d'Elara assis a cote terrifie mais indemne. Le chariot contient des marchandises precieuses pour le village.",
            "description_en": "You find the overturned cart and Elara's son sitting beside it terrified but unharmed. The cart contains valuable goods for the village.",
            "choice_a": {
                "label_fr": "Lui montrer le chemin. Sa mere l'attend.",
                "label_en": "Show him the way. His mother is waiting.",
                "stat": "compassion",
                "value": 1
            },
            "choice_b": {
                "label_fr": "Prendre les marchandises. Le village en a besoin.",
                "label_en": "Take the goods. The village needs them.",
                "stat": "severite",
                "value": 1
            }
        }
        break

with open('world/quests.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f"Updated {updated} quests with dialogues")
print("Added moral choice to q_side_elara_chariot")
