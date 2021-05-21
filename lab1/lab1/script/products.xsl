<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml"
  doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"
  doctype-public="-//W3C//DTD XHTML 1.1//EN" indent="yes"/>

  <xsl:template match="/">
    <html>
      <head>
        <title>
          Products
        </title>
      </head>
      <body>
        <h1>
          Products Table
        </h1>
        <table>
          <tr>
            <td>Name</td>
            <td>Price</td>
            <td>Src</td>
          </tr>
          <xsl:apply-templates/>
        </table>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="item">
    <tr>
     <td>
         <xsl:value-of select="title"/>
         <br/>
         <xsl:element name="img">
             <xsl:attribute name="src">
                 <xsl:value-of select="img"/>
             </xsl:attribute>
         </xsl:element>
     </td>
     <td><xsl:value-of select="price"/></td>
     <td><xsl:value-of select="src"/></td>
    </tr>
  </xsl:template>

</xsl:stylesheet>