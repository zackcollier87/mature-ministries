<?php
/** Catalog template — ruled sermon list with client-side search + series filter. */
if ( ! defined( 'ABSPATH' ) ) exit;
get_header();

$total   = mm_sermon_count();
$series  = get_terms( array( 'taxonomy' => 'mm_series', 'hide_empty' => true, 'orderby' => 'name' ) );

$q = new WP_Query( array(
	'post_type'      => 'mm_sermon',
	'posts_per_page' => -1,
	'orderby'        => 'meta_value',
	'meta_key'       => 'mm_sermon_date',
	'order'          => 'DESC',
) );
?>

<section class="container catalog-head">
	<p class="mono catalog-head__tag">CATALOG</p>
	<h1>Every entry, in order.</h1>
	<p class="catalog-head__count mono tabular-nums" data-count><?php echo esc_html( $total ); ?> sermons</p>
</section>

<section class="container controls">
	<input type="search" id="mm-search" class="mono" placeholder="Search title, scripture, or series&hellip;" aria-label="Search sermons" />
	<select id="mm-series-filter" class="mono" aria-label="Filter by series">
		<option value="">All series</option>
		<?php if ( ! is_wp_error( $series ) ) foreach ( $series as $term ) : ?>
			<option value="<?php echo esc_attr( $term->name ); ?>"><?php echo esc_html( $term->name ); ?></option>
		<?php endforeach; ?>
	</select>
</section>

<section class="container">
	<p id="mm-empty-state" class="empty-state mono" hidden>No sermons match your search.</p>
	<ol class="catalog" id="mm-catalog-list">
		<?php while ( $q->have_posts() ) : $q->the_post();
			$id      = get_the_ID();
			$date    = get_post_meta( $id, 'mm_sermon_date', true );
			$yt      = get_post_meta( $id, 'mm_youtube_id', true );
			$guides  = mm_get_guides( $id );
			$terms   = get_the_terms( $id, 'mm_series' );
			$term_names = ( ! empty( $terms ) && ! is_wp_error( $terms ) ) ? wp_list_pluck( $terms, 'name' ) : array();
			$search_blob = strtolower( get_the_title() . ' ' . implode( ' ', $term_names ) );
			?>
			<li class="catalog-row"
				data-series="<?php echo esc_attr( implode( '|', $term_names ) ); ?>"
				data-search="<?php echo esc_attr( $search_blob ); ?>">
				<a href="<?php the_permalink(); ?>" class="catalog-row__link">
					<span class="catalog-row__date mono tabular-nums"><?php echo esc_html( $date ? date_i18n( 'M d, Y', strtotime( $date ) ) : '' ); ?></span>
					<span class="catalog-row__main">
						<span class="catalog-row__title"><?php the_title(); ?></span>
						<?php if ( ! empty( $term_names ) ) : ?>
							<span class="catalog-row__series mono"><?php echo esc_html( implode( ' · ', $term_names ) ); ?></span>
						<?php endif; ?>
					</span>
					<span class="catalog-row__meta mono">
						<?php if ( $yt ) : ?><span class="badge badge--video">VIDEO</span><?php endif; ?>
						<?php if ( ! empty( $guides ) ) : ?>
							<span class="badge"><?php echo esc_html( count( $guides ) ); ?> GUIDE<?php echo count( $guides ) > 1 ? 'S' : ''; ?></span>
						<?php endif; ?>
					</span>
				</a>
			</li>
		<?php endwhile; wp_reset_postdata(); ?>
	</ol>
</section>

<?php get_footer(); ?>
