from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Q

class Command(BaseCommand):
    help = 'Supprime tous les utilisateurs sauf le superutilisateur principal (si spécifié)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exclude-superusers',
            action='store_true',
            help='Exclure les superutilisateurs de la suppression',
        )
        parser.add_argument(
            '--exclude-staff',
            action='store_true',
            help='Exclure les membres du staff de la suppression',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les utilisateurs qui seraient supprimés sans effectuer la suppression',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprime les utilisateurs sans confirmation',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.all()
        
        # Exclure les superutilisateurs si demandé
        if options['exclude_superusers']:
            users = users.filter(is_superuser=False)
            self.stdout.write(self.style.NOTICE("Les superutilisateurs seront conservés"))
            
        # Exclure les membres du staff si demandé
        if options['exclude_staff']:
            users = users.filter(is_staff=False)
            self.stdout.write(self.style.NOTICE("Les membres du staff seront conservés"))

        # Compter les utilisateurs à supprimer
        count = users.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("Aucun utilisateur à supprimer."))
            return
            
        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f"Mode test: {count} utilisateurs seraient supprimés :"))
            for user in users[:5]:  # Afficher les 5 premiers utilisateurs comme exemple
                self.stdout.write(f"- {user.username} ({user.email})")
            if count > 5:
                self.stdout.write(f"... et {count - 5} autres utilisateurs")
            return
            
        # Vérifier si on est en mode force
        if not options['force']:
            # Demander confirmation
            self.stdout.write(self.style.WARNING(f"Vous êtes sur le point de supprimer {count} utilisateurs."))
            confirm = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ")
            if confirm.lower() != 'oui':
                self.stdout.write(self.style.ERROR("Opération annulée par l'utilisateur"))
                return
        
        # Afficher un compte à rebours
        self.stdout.write(self.style.WARNING(f"Suppression de {count} utilisateurs en cours..."))
        
        # Supprimer les utilisateurs
        deleted_count, _ = users.delete()
        
        # Afficher un message de confirmation
        self.stdout.write(self.style.SUCCESS(f"{deleted_count} utilisateurs ont été supprimés avec succès."))
        
        # Avertissement si des utilisateurs n'ont pas été supprimés
        if deleted_count < count:
            self.stdout.write(self.style.WARNING(f"Note: {count - deleted_count} utilisateurs n'ont pas pu être supprimés."))
