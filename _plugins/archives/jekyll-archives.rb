# frozen_string_literal: true

require "jekyll"

module Jekyll
  module Archives
    # Internal requires
    autoload :Archive,  "jekyll-archives/archive"
    autoload :PageDrop, "jekyll-archives/page_drop"

    class Archives < Jekyll::Generator
      safe true

      DEFAULTS = {
        "layout"     => "archive",
        "enabled"    => [],
        "permalinks" => {
          "year"     => "/:year/",
          "month"    => "/:year/:month/",
          "day"      => "/:year/:month/:day/",
          "tag"      => "/tag/:name/",
          "category" => "/category/:name/",
        },
        # TODO: extend to support archives per collection
        "collection" => "posts",
      }.freeze

      def initialize(config = {})
        archives_config = config.fetch("jekyll-archives", {})
        if archives_config.is_a?(Hash)
          @config = Utils.deep_merge_hashes(DEFAULTS, archives_config)
        else
          @config = nil
          Jekyll.logger.warn "Archives:", "Expected a hash but got #{archives_config.inspect}"
          Jekyll.logger.warn "", "Archives will not be generated for this site."
        end
        @enabled = @config && @config["enabled"]
      end

      def generate(site)
        return if @config.nil?

        @site = site
        @posts = site.collections[@config["collection"]]
        @archives = []

        @site.config["jekyll-archives"] = @config

        read
        @site.pages.concat(@archives)

        @site.config["archives"] = @archives
      end

      # Read archive data from posts
      def read
        read_tags
        read_categories
        read_dates
      end

      def read_tags
        if enabled? "tags"
          tags.each do |title, posts|
            @archives << Archive.new(@site, title, "tag", posts)
          end
        end
      end

      def read_categories
        if enabled? "categories"
          categories.each do |title, posts|
            @archives << Archive.new(@site, title, "category", posts)
          end
        end
      end

      def read_dates
        y_archives = []
        m_archives = []
        d_archives = []
        years.each do |year, y_posts|
          append_enabled_date_type({ :year => year }, "year", y_posts, y_archives)
          months(y_posts).each do |month, m_posts|
            append_enabled_date_type({ :year => year, :month => month }, "month", m_posts, m_archives)
            days(m_posts).each do |day, d_posts|
              append_enabled_date_type({ :year => year, :month => month, :day => day }, "day", d_posts, d_archives)
            end
          end
        end

        [y_archives, m_archives, d_archives].each do |arr|
          arr.each_with_index do |archive, idx|
            archive.previous = arr[idx - 1] if archive != arr.first
            archive.next = arr[idx + 1] if archive != arr.last
          end
        end
      end

      # Checks if archive type is enabled in config
      def enabled?(archive)
        @enabled == true || @enabled == "all" || (@enabled.is_a?(Array) && @enabled.include?(archive))
      end

      def tags
        @site.tags
      end

      def categories
        @site.categories
      end

      # Custom `post_attr_hash` method for years
      def years
        date_attr_hash(@posts.docs, "%Y")
      end

      # Custom `post_attr_hash` method for months
      def months(year_posts)
        date_attr_hash(year_posts, "%m")
      end

      # Custom `post_attr_hash` method for days
      def days(month_posts)
        date_attr_hash(month_posts, "%d")
      end

      private

      # Initialize a new Archive page and append to base array if the associated date `type`
      # has been enabled by configuration.
      #
      # meta          - A Hash of the year / month / day as applicable for date.
      # type          - The type of date archive.
      # posts         - The array of posts that belong in the date archive.
      # archives_part - The array of archives that the added archive shuold be added to.
      def append_enabled_date_type(meta, type, posts, archives_part)
        if enabled?(type)
          archive = Archive.new(@site, meta, type, posts)
          @archives << archive
          archives_part << archive
        end
      end

      # Custom `post_attr_hash` for date type archives.
      #
      # posts - Array of posts to be considered for archiving.
      # id    - String used to format post date via `Time.strptime` e.g. %Y, %m, etc.
      def date_attr_hash(posts, id)
        hash = Hash.new { |hsh, key| hsh[key] = [] }
        posts.each { |post| hash[post.date.strftime(id)] << post }
        hash.each_value { |posts| posts.sort!.reverse! }
        hash
      end
    end
  end
end
