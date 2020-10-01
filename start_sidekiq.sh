#!/bin/bash

echo "Running sidekiq..."
bundle exec sidekiq -C config/sidekiq.yml
