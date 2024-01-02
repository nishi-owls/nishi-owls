# frozen_string_literal: true

module Jekyll
  module Archives
    class PageDrop < Jekyll::Drops::Drop
      extend Forwardable

      mutable false

      def_delegators :@obj, :posts, :type, :title, :date, :name, :path, :url, :permalink
      def_delegators :@obj, :next, :previous
      private def_delegator :@obj, :data, :fallback_data
    end
  end
end
