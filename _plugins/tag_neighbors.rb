# Custom Jekyll plugin to find the adjacent post sharing a tag
#
# Usage:
#   {% assign p_post = page | previous_in_tag: "news" %}  # Older post tagged "news"
#   {% assign n_post = page | next_in_tag: "news" %}      # Newer post tagged "news"
#
# Returns nil when there is no such post.
module Jekyll
  module TagNeighborsFilter
    def previous_in_tag(page, tag)
      tag_neighbor(page, tag, -1)
    end

    def next_in_tag(page, tag)
      tag_neighbor(page, tag, 1)
    end

    private

    def tag_neighbor(page, tag, offset)
      posts = @context.registers[:site].posts.docs.select do |post|
        Array(post.data["tags"]).include?(tag)
      end
      index = posts.index { |post| post.url == page["url"] }
      return nil unless index

      neighbor_index = index + offset
      return nil if neighbor_index.negative?

      posts[neighbor_index]&.to_liquid
    end
  end
end

Liquid::Template.register_filter(Jekyll::TagNeighborsFilter)
