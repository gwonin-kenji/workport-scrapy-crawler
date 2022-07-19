cat /dev/null > /var/spool/mail/ec2-user
cd /home/ec2-user/workport-scrapy-crawler
make update_all_companies
make update_all_job_offers
