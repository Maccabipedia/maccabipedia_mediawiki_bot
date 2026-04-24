FROM php:7.4.33-apache-bullseye

ENV MW_VERSION=1.39.11 \
    APCU_VERSION=5.1.24 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        libicu-dev \
        libpng-dev \
        libjpeg-dev \
        libfreetype6-dev \
        libzip-dev \
        libonig-dev \
        unzip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" \
        calendar \
        gd \
        intl \
        mbstring \
        mysqli \
        opcache \
        zip

RUN pecl install "apcu-${APCU_VERSION}" && docker-php-ext-enable apcu

RUN a2enmod rewrite

RUN curl -fSL "https://releases.wikimedia.org/mediawiki/1.39/mediawiki-${MW_VERSION}.tar.gz" -o /tmp/mediawiki.tar.gz \
    && tar -xzf /tmp/mediawiki.tar.gz --strip-components=1 -C /var/www/html \
    && rm /tmp/mediawiki.tar.gz \
    && chown -R www-data:www-data /var/www/html

WORKDIR /var/www/html

COPY entrypoint.sh /usr/local/bin/mw-entrypoint.sh
RUN chmod +x /usr/local/bin/mw-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/mw-entrypoint.sh"]
CMD ["apache2-foreground"]
