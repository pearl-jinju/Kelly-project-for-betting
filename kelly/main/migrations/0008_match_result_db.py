# Generated by Django 5.0.4 on 2024-05-01 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_matchdb_handicap_value_matchdb_under_over_value_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match_RESULT_DB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.TextField(default='-')),
                ('date', models.TextField(default='-')),
                ('end_time', models.TextField(default='-')),
                ('betting_type', models.TextField(default='-')),
                ('home_team', models.TextField(default='-')),
                ('away_team', models.TextField(default='-')),
                ('odd_list', models.TextField(default='-')),
                ('prob_from_odd_list', models.TextField(default='-')),
                ('betting_sports', models.TextField(default='-')),
                ('league_name', models.TextField(default='-')),
                ('handicap_value', models.TextField(default=0)),
                ('under_over_value', models.TextField(default=0)),
                ('match_result', models.TextField(default=0)),
                ('march_winner', models.TextField(default=0)),
            ],
        ),
    ]
