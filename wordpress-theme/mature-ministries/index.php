<?php
/** Generic fallback template (search results, 404, anything without a dedicated template). */
if ( ! defined( 'ABSPATH' ) ) exit;
get_header();
?>
<div class="container" style="padding-block: 48px 96px;">
	<?php if ( have_posts() ) : ?>
		<ol class="catalog">
			<?php while ( have_posts() ) : the_post(); ?>
				<li class="catalog-row">
					<a href="<?php the_permalink(); ?>" class="catalog-row__link">
						<span class="catalog-row__main">
							<span class="catalog-row__title"><?php the_title(); ?></span>
						</span>
					</a>
				</li>
			<?php endwhile; ?>
		</ol>
	<?php else : ?>
		<p class="mono">Nothing found.</p>
	<?php endif; ?>
</div>
<?php get_footer(); ?>
