#!/bin/bash

echo "Executing database migrations..."
bundle exec rake db:migrate

echo "Seeding db..."
bundle exec rake db:seed

echo "Start app..."
bundle exec rails server -b 0.0.0.0