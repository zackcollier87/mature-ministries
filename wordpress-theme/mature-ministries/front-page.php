<?php
/**
 * Home template — ledger-style masthead + recent-entries ledger.
 * Direction: "Pulpit Card Catalog" (see DESIGN.md in the project repo).
 */
if ( ! defined( 'ABSPATH' ) ) exit;
get_header();

$total = mm_sermon_count();

$recent_q = new WP_Query( array(
	'post_type'      => 'mm_sermon',
	'posts_per_page' => 3,
	'orderby'        => 'meta_value',
	'meta_key'       => 'mm_sermon_date',
	'order'          => 'DESC',
) );

$series_terms  = get_terms( array( 'taxonomy' => 'mm_series', 'hide_empty' => true ) );
$series_count  = is_array( $series_terms ) ? count( $series_terms ) : 0;

$last_date_q = new WP_Query( array(
	'post_type' => 'mm_sermon', 'posts_per_page' => 1,
	'orderby' => 'meta_value', 'meta_key' => 'mm_sermon_date', 'order' => 'DESC',
) );
$first_date_q = new WP_Query( array(
	'post_type' => 'mm_sermon', 'posts_per_page' => 1,
	'orderby' => 'meta_value', 'meta_key' => 'mm_sermon_date', 'order' => 'ASC',
) );
$last_date  = $last_date_q->have_posts() ? get_post_meta( $last_date_q->posts[0]->ID, 'mm_sermon_date', true ) : '';
$first_date = $first_date_q->have_posts() ? get_post_meta( $first_date_q->posts[0]->ID, 'mm_sermon_date', true ) : '';
?>

<section class="masthead">
	<div class="container masthead__row">
		<p class="mono masthead__tag">SERMON ARCHIVE &middot; EST. RECORD <?php echo esc_html( $first_date ? date_i18n( 'M d, Y', strtotime( $first_date ) ) : '' ); ?></p>
		<h1 class="masthead__title">A complete, ordered record<br />of Pastor Wayne Edwards&rsquo; preaching.</h1>
		<div class="masthead__stats mono">
			<span><strong class="tabular-nums"><?php echo esc_html( $total ); ?></strong> sermons</span>
			<span class="masthead__dot">&middot;</span>
			<span><strong class="tabular-nums"><?php echo esc_html( $series_count ); ?></strong> series</span>
			<span class="masthead__dot">&middot;</span>
			<span>through <strong><?php echo esc_html( $last_date ? date_i18n( 'M d, Y', strtotime( $last_date ) ) : '' ); ?></strong></span>
		</div>
	</div>
</section>

<section class="container split" id="about">
	<div class="split__prose">
		<h2>Why this archive exists</h2>
		<p>
			Every message preached at Heritage Baptist Church &mdash; the video, the full transcript, and the
			printed study guide in five languages &mdash; kept in one place that belongs to the pastor himself,
			independent of any one church's website or hosting.
		</p>
		<p>
			Nothing here is summarized or excerpted. Each entry is the sermon as originally delivered and
			published, indexed by date, series, and scripture, and searchable in full.
		</p>
		<a class="btn" href="<?php echo esc_url( get_post_type_archive_link( 'mm_sermon' ) ); ?>">Browse the full catalog &rarr;</a>
	</div>

	<div class="split__ledger">
		<p class="ledger__label mono">RECENT ENTRIES</p>
		<ol class="ledger">
			<?php while ( $recent_q->have_posts() ) : $recent_q->the_post();
				$date  = get_post_meta( get_the_ID(), 'mm_sermon_date', true );
				$terms = get_the_terms( get_the_ID(), 'mm_series' );
				?>
				<li class="ledger__row">
					<a href="<?php the_permalink(); ?>">
						<span class="ledger__date mono tabular-nums"><?php echo esc_html( $date ? date_i18n( 'M d, Y', strtotime( $date ) ) : '' ); ?></span>
						<span class="ledger__title"><?php the_title(); ?></span>
						<?php if ( ! empty( $terms ) && ! is_wp_error( $terms ) ) : ?>
							<span class="ledger__series mono"><?php echo esc_html( $terms[0]->name ); ?></span>
						<?php endif; ?>
					</a>
				</li>
			<?php endwhile; wp_reset_postdata(); ?>
		</ol>
	</div>
</section>

<?php get_footer(); ?>
