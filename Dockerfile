# Base stage =====================================================================================
FROM ruby:2.6.3-buster AS base

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN gem install bundler

WORKDIR /code

COPY Gemfile* ./
RUN bundle install
EXPOSE 3000

# Production stage =============================================================================
FROM base AS production
# here you can install dependencies that are specific for prod

# This should change in real prod environment as we don't want to put everything on the server
COPY . .

ENTRYPOINT ["sh", "/code/entrypoint.sh"]

# Development stage =============================================================================
FROM base AS development
# here you can install dependencies that are specific for prod

COPY . .

ENTRYPOINT ["sh", "/code/entrypoint.sh"]

# Run only on development (not recomended for the production)
CMD ["sh", "/code/start.sh"]
